# 文献检索功能
## 1. 加载模型
将sbert模型文件放在`source/retrieval/`目录下
```python
from source.retrieval.similar_model import SimilarModel
mdl = SimilarModel('source/retrieval/sbert')
```
## 2. 检索
模型API如下：
```python
    def crawler(self,
                query: str,
                instruct: Union[str, None] = None,
                start_year: Union[str, None] = None,
                end_year: Union[str, None] = None,
                max_capacity: int = 50,
                target_capacity: int = 10,
                debug_mode: bool = False,
                retry_times: int = 3) -> List[List[str]]:
```
- query：查询句子，一般从pdf文档中划词选择
- instruct: 文档中参考的段落，一般是文档前100个单词
- start_year: 搜索文档的开始时间
- end_year: 搜索文档的结束时间
- max_capacity: 搜索文档的最大数量
- target_capacity: 返回文档的最大数量
- debug_mode: 是否开启调试模式
- retry_times: 重试的次数

例：
```python
mdl.crawler("abc", "xyz")
```
