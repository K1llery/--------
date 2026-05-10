from __future__ import annotations

import heapq
from collections import Counter
from dataclasses import dataclass, field

"""
文本压缩模块。提供基于哈夫曼编码（Huffman Coding）的无损压缩与解码能力。
"""


@dataclass(order=True)
class HuffmanNode:
    """哈夫曼树的节点类。用于构建无损压缩的哈夫曼树。"""
    weight: int
    char: str | None = field(compare=False, default=None)
    left: "HuffmanNode | None" = field(compare=False, default=None)
    right: "HuffmanNode | None" = field(compare=False, default=None)


class HuffmanCodec:
    """哈夫曼编码解码器，提供无损压缩方案的相关操作。"""
    def build_tree(self, text: str) -> HuffmanNode | None:
        """
        根据输入文本构建哈夫曼树。
        
        :param text: 需要压缩的原始文本
        :return: 哈夫曼树的根节点，如果文本为空则返回None
        """
        if not text:
            return None
        queue = [HuffmanNode(weight, char=char) for char, weight in Counter(text).items()]
        heapq.heapify(queue)
        while len(queue) > 1:
            left = heapq.heappop(queue)
            right = heapq.heappop(queue)
            heapq.heappush(queue, HuffmanNode(left.weight + right.weight, left=left, right=right))
        return queue[0]

    def build_codes(self, root: HuffmanNode | None) -> dict[str, str]:
        """
        通过遍历哈夫曼树生成每个字符的编码表。
        
        :param root: 哈夫曼树的根节点
        :return: 字符到二进制字符串编码的映射字典
        """
        if root is None:
            return {}
        codes: dict[str, str] = {}

        def dfs(node: HuffmanNode, prefix: str) -> None:
            if node.char is not None:
                codes[node.char] = prefix or "0"
                return
            dfs(node.left, prefix + "0")
            dfs(node.right, prefix + "1")

        dfs(root, "")
        return codes

    def encode(self, text: str) -> tuple[str, dict[str, str]]:
        """
        将文本压缩为哈夫曼编码。
        
        :param text: 原始文本
        :return: 压缩后的二进制字符串以及解码用的编码字典表
        """
        tree = self.build_tree(text)
        codes = self.build_codes(tree)
        encoded = "".join(codes[ch] for ch in text)
        return encoded, codes

    def decode(self, encoded: str, codes: dict[str, str]) -> str:
        """
        将哈夫曼编码字符串解码还原为原始文本。
        
        :param encoded: 压缩后的二进制字符串
        :param codes: 编码表映射
        :return: 还原的原始文本
        """
        reverse = {value: key for key, value in codes.items()}
        cursor = ""
        output = []
        for bit in encoded:
            cursor += bit
            if cursor in reverse:
                output.append(reverse[cursor])
                cursor = ""
        return "".join(output)
