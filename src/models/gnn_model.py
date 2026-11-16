import os
import copy
import logging
from typing import Dict, Any, Tuple

import torch
import torch.nn as nn
import torch.nn.functional as F

try:
    import dgl
    import dgl.nn as dglnn
    DGL_AVAILABLE = True
except ImportError:
    DGL_AVAILABLE = False

logger = logging.getLogger(__name__)

class PhishRGCN(nn.Module):
    """
    Relational Graph Convolutional Network for Phishing Domain Detection.
    Nodes: domains, IPs, nameservers
    Relations: has_ip, ip_of, has_ns, ns_of, self
    """
    def __init__(self, in_feats: Dict[str, int], hidden_dim: int = 128, 
                 num_classes: int = 2, num_layers: int = 3, dropout: float = 0.3, num_bases: int = -1):
        super(PhishRGCN, self).__init__()
        
        if not DGL_AVAILABLE:
            raise RuntimeError("DGL is required to instantiate PhishRGCN.")
            
        self.hidden_dim = hidden_dim
        self.num_layers = num_layers
        
        self.etypes = ['has_ip', 'ip_of', 'has_ns', 'ns_of', 'self']
        
        self.projections = nn.ModuleDict({
            ntype: nn.Linear(dim, hidden_dim) for ntype, dim in in_feats.items()
        })
        
        self.layers = nn.ModuleList()
        self.batch_norms = nn.ModuleList()
        
        for i in range(num_layers):
            self.layers.append(dglnn.HeteroGraphConv({
                rel: dglnn.GraphConv(hidden_dim, hidden_dim, norm='right', weight=True, bias=True)
                for rel in self.etypes
            }, aggregate='sum'))
            
            self.batch_norms.append(nn.ModuleDict({
                ntype: nn.BatchNorm1d(hidden_dim) for ntype in in_feats.keys()
            }))
            
        self.dropout = nn.Dropout(dropout)
        
        self.classifier = nn.Sequential(
            nn.Linear(hidden_dim, hidden_dim // 2),
            nn.ReLU(),
            nn.Dropout(dropout),
            nn.Linear(hidden_dim // 2, num_classes)
        )

    def forward(self, g, x_dict: Dict[str, torch.Tensor]) -> torch.Tensor:
        h_dict = {
            ntype: F.relu(self.projections[ntype](x)) for ntype, x in x_dict.items()
        }
        
        for i in range(self.num_layers):
            h_dict = self.layers[i](g, h_dict)
            
            for ntype in h_dict.keys():
                h_dict[ntype] = self.batch_norms[i][ntype](h_dict[ntype])
                h_dict[ntype] = F.relu(h_dict[ntype])
                h_dict[ntype] = self.dropout(h_dict[ntype])
                
        domain_h = h_dict['domain']
        logits = self.classifier(domain_h)
        return logits

class FocalLoss(nn.Module):
    """
    Focal Loss for handling class imbalance.
    FL(p_t) = -alpha_t * (1 - p_t)^gamma * log(p_t)
    """
    def __init__(self, alpha: float = 0.25, gamma: float = 2.0, reduction: str = 'mean') -> None:
        super(FocalLoss, self).__init__()
        self.alpha = alpha
        self.gamma = gamma
        self.reduction = reduction

    def forward(self, logits: torch.Tensor, targets: torch.Tensor) -> torch.Tensor:
        ce_loss = F.cross_entropy(logits, targets, reduction='none')
        pt = torch.exp(-ce_loss)
        focal_loss = (self.alpha * (1 - pt) ** self.gamma * ce_loss)
        
        if self.reduction == 'mean': return focal_loss.mean()
        elif self.reduction == 'sum': return focal_loss.sum()
        else: return focal_loss


class EarlyStopping:
    """Early stops the training if validation loss doesn't improve after a given patience."""
    def __init__(self, patience: int = 20, min_delta: float = 0.001, path: str = 'best_model.pt') -> None:
        self.patience = patience
        self.min_delta = min_delta
        self.path = path
        self.counter = 0
        self.best_loss = None
        self.early_stop = False
        self.best_state = None

    def __call__(self, val_loss: float, model: nn.Module, epoch: int) -> bool:
        if self.best_loss is None:
            self.best_loss = val_loss
            self.save_checkpoint(model)
        elif val_loss > self.best_loss - self.min_delta:
            self.counter += 1
            if self.counter >= self.patience:
                self.early_stop = True
        else:
            self.best_loss = val_loss
            self.save_checkpoint(model)
            self.counter = 0
        return self.early_stop

    def save_checkpoint(self, model: nn.Module) -> None:
        self.best_state = copy.deepcopy(model.state_dict())
        try:
            torch.save(model.state_dict(), self.path)
        except Exception as e:
            logger.warning(f"Failed to save early stopping checkpoint to {self.path}: {e}")

    def load_best_model(self, model: nn.Module) -> nn.Module:
        if self.best_state is not None:
            model.load_state_dict(self.best_state)
        elif os.path.exists(self.path):
            model.load_state_dict(torch.load(self.path))
        return model
