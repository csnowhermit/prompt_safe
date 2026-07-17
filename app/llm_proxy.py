import asyncio

from app.config import settings
from app.logger import logger


class LLMProxy:
    def __init__(self):
        pass

    async def forward(self, prompt: str, model: str = None) -> str:
        await asyncio.sleep(0.1)
        
        responses = {
            "请帮我写一首关于春天的诗": "春天来了，万物复苏，小草破土而出，花儿争相开放，鸟儿在枝头欢快地歌唱，处处洋溢着生机与希望。",
            "Python中如何实现快速排序算法？": "快速排序是一种高效的排序算法，采用分治策略。基本思路是选择一个基准元素，将数组分为两部分，使得左边都小于基准，右边都大于基准，然后递归排序。",
            "请把以下英文翻译成中文：Hello World": "你好，世界！",
            "今天天气怎么样？": "抱歉，我无法获取实时天气信息。建议您查看天气预报应用或网站。",
            "请解释什么是机器学习": "机器学习是人工智能的一个分支，它使计算机系统能够从数据中学习并改进性能，而无需进行明确编程。",
            "给我讲个笑话": "为什么程序员喜欢用黑暗模式？因为光会吸引虫子（bug）！",
            "1+1等于几？": "1+1等于2。",
            "推荐几本好书": "推荐几本经典书籍：《人类简史》、《百年孤独》、《活着》、《三体》系列、《思考，快与慢》。",
            "如何提高英语口语水平？": "提高英语口语需要多听多说，可以通过看英文电影、听英文歌曲、参加语言交换活动等方式练习。",
            "你好": "你好！有什么我可以帮助你的吗？",
        }

        if prompt in responses:
            return responses[prompt]
        
        return f"这是针对您请求的模拟响应。您的输入是：{prompt[:50]}..."