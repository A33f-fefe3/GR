from neo4j import GraphDatabase
from yfiles_jupyter_graphs import GraphWidget
import os


os.environ["NEO4J_URI"] = "bolt://localhost:7687"
os.environ["NEO4J_USERNAME"] = "neo4j"
os.environ["NEO4J_PASSWORD"] = "12345678"

def clean_node(node):
    # 清理空标签或包含非法字符的标签
    if not node.type or any(ord(c) == 0 for c in node.type):
        # 如果标签为空或包含非法字符，可以设置一个默认标签
        # node.type = "DefaultLabel"  # 设置一个默认标签
        # 或者可以选择抛出异常或记录日志
        raise ValueError(f"Invalid label found: {node.type}")
    return node

def clean_graph_document(graph_doc):
    # 遍历文档中的所有节点并清理标签
    graph_doc.nodes = [clean_node(node) for node in graph_doc.nodes]
    return graph_doc




def showGraph():
    # 使用 with 语句确保 Driver 和 Session 被正确关闭
    with GraphDatabase.driver(
        uri=os.environ["NEO4J_URI"],
        auth=(os.environ["NEO4J_USERNAME"], os.environ["NEO4J_PASSWORD"])
    ) as driver:
        with driver.session() as session:
            # 执行查询并获取图数据
            graph_data = session.run("MATCH (s)-[r:!MENTIONS]->(t) RETURN s, r, t").graph()
            
            # 假设 GraphWidget 是一个自定义类或库中的类，用于展示图数据
            widget = GraphWidget(graph=graph_data)
            widget.node_label_mapping = 'id'
            
            # 返回 widget 以便可以在其他地方使用
            return widget