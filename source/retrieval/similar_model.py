from typing import List, Union

from sentence_transformers import SentenceTransformer, util
from source.retrieval.crawlers import get_paper_list_by_keywork


class SimilarModel:
    def __init__(self, name_or_path: str) -> None:
        self.model = SentenceTransformer(name_or_path)

    def cos_sim(self, sen1: str, sen2: str):
        emb1 = self.model.encode(sen1)
        emb2 = self.model.encode(sen2)
        cosin_sim = util.pytorch_cos_sim(emb1, emb2)
        return cosin_sim.item()

    def crawler(self,
                query: str,
                instruct: Union[str, None] = None,
                start_year: Union[str, None] = None,
                end_year: Union[str, None] = None,
                max_capacity: int = 50,
                target_capacity: int = 10,
                debug_mode: bool = False,
                retry_times: int = 3) -> List[List[str]]:
        """
        !!! 需要设置代理
        用于搜索文章
        query是查询的句子，
        instruct是参考排序的句子（为空则不排序），
        max_capacity是从谷歌学术中爬取的文章数，
        target_capacity是返回的文章数。
        返回[[论文标题, 引用数, 发表时间及机构缩写, 论文链接]...]
        """
        out = get_paper_list_by_keywork(keyword=query,
                                        start_year=start_year,
                                        end_year=end_year,
                                        max_capacity=max_capacity,
                                        debug_mode=debug_mode,
                                        retry_times=retry_times)
        if not instruct:
            return out
        rec_sort = [[self.cos_sim(instruct, rec[0])] + rec for rec in out]
        rec_sort.sort(key=lambda item: -item[0])
        return [item[1:] for item in rec_sort[:target_capacity]]
