from torch.utils.data import Dataset, DataLoader
import torch


class NumpyDataset(Dataset):
    def __init__(self, x, y):
        super().__init__()
        self.x = torch.from_numpy(x).float()
        self.y = torch.from_numpy(y).float()

    def __getitem__(self, idx):
        return self.x[idx], self.y[idx]

    def __len__(self):
        return len(self.x)


class BertDataset(Dataset):
    def __init__(self, x, y, tokenizer, length=128):
        super(BertDataset, self).__init__()
        self.tokenizer = tokenizer
        self.length = length
        self.x = x
        self.y = torch.tensor(y)
        self.tokens_cache = {}

    def tokenize(self, x):
        dic = self.tokenizer.batch_encode_plus(
                    [x],        # input must be a list
                    max_length=self.length,
                    padding='max_length',
                    truncation=True,
                    return_token_type_ids=True,
                    return_tensors="pt"
                )
        return [x[0] for x in dic.values()]     # get rid of the first dim

    def __getitem__(self, idx):
        if idx not in self.tokens_cache:
            self.tokens_cache[idx] = self.tokenize(self.x[idx])
        input_ids, token_type_ids, attention_mask = self.tokens_cache[idx]
        return input_ids, token_type_ids, attention_mask, self.y[idx]

    def __len__(self):
        return len(self.y)


class EnsembleDataset(Dataset):
    def __init__(self, x_style, x_char, x_bert, y):
        super(EnsembleDataset, self).__init__()
        self.x_style = x_style
        self.x_char = x_char
        self.x_bert = x_bert
        self.y = y
    
    def __getitem__(self, idx):
        return self.x_style[idx], self.x_char[idx], torch.tensor(self.x_bert['input_ids'][idx]), torch.tensor(self.x_bert['attention_mask'][idx]), self.y[idx]

    def __len__(self):
        return len(self.y)

class TransformerEnsembleDataset(Dataset):
    def __init__(self, x, y, tokenizers, lengths):
        super(TransformerEnsembleDataset, self).__init__()
        self.x = x
        self.tokenizers = tokenizers
        self.lengths = lengths
        self.caches = [{} for i in range(len(tokenizers))]
        # self.tk1 = tk1
        # self.tk2 = tk2 
        # self.tk3 = tk3
        # self.tk4 = tk4
        # self.cache1 = {}
        # self.cache2 = {}
        # self.cache3 = {}
        # self.cache4 = {}
        self.y = torch.tensor(y)

    def tokenize(self, x, i):
        dic = self.tokenizers[i].batch_encode_plus(
                    batch_text_or_text_pairs=[x],        # input must be a list
                    max_length=self.lengths[i],
                    padding='max_length',
                    truncation=True,
                    return_token_type_ids=True,
                    return_tensors="pt"
                )
        return [x[0] for x in dic.values()]     # get rid of the first dim
    
    def __getitem__(self, idx):
        if idx not in self.caches[0]:
            for i in range(len(self.tokenizers)):
                self.caches[i][idx] = self.tokenize(self.x[idx], i)
        
        return [self.caches[i][idx] for i in range(len(self.tokenizers))], self.y[idx]

        # i1, t1, a1 = self.x1['input_ids'][idx], self.x1['token_type_ids'][idx], self.x1['attention_mask'][idx]
        # i2, t2, a2 = self.x2['input_ids'][idx], self.x2['token_type_ids'][idx], self.x2['attention_mask'][idx]
        # i3, t3, a3 = self.x3['input_ids'][idx], self.x3['token_type_ids'][idx], self.x3['attention_mask'][idx]
        # i4, t4, a4 = self.x4['input_ids'][idx], self.x4['token_type_ids'][idx], self.x4['attention_mask'][idx]
        # return [i1, t1, a1], [i2, t2, a2], [i3, t3, a3], [i4, t4, a4], self.y[idx]

    def __len__(self):
        return len(self.y)