import os
from neo4j import GraphDatabase
import pandas as pd

os.environ["NEO4J_URI"] = "bolt://localhost:7687"
os.environ["NEO4J_USERNAME"] = "neo4j"
os.environ["NEO4J_PASSWORD"] = "12345678"

def create_fulltext_index():
    driver = GraphDatabase.driver(
        uri=os.environ["NEO4J_URI"],
        auth=(os.environ["NEO4J_USERNAME"], os.environ["NEO4J_PASSWORD"])
    )
    
    with driver.session() as session:
        # 创建全文索引
        session.run(
            """
            CREATE FULLTEXT INDEX entity IF NOT EXISTS FOR (e:__Entity__) ON EACH [e.id]
            """
        )

def export_all_relationships_to_csv():
    driver = GraphDatabase.driver(
        uri=os.environ["NEO4J_URI"],
        auth=(os.environ["NEO4J_USERNAME"], os.environ["NEO4J_PASSWORD"])
    )
    with driver.session() as session:
        # 查询所有关系数据（排除 MENTIONS 关系）
        result = session.run(
            """
            MATCH (n)-[r]->(neighbor)
            WHERE NOT type(r) = 'MENTIONS'
            RETURN n.id AS source, type(r) AS relationship, neighbor.id AS target
            UNION
            MATCH (n)<-[r]-(neighbor)
            WHERE NOT type(r) = 'MENTIONS'
            RETURN neighbor.id AS source, type(r) AS relationship, n.id AS target
            """
        )
        # 提取查询结果
        data = [(record['source'], record['relationship'], record['target']) for record in result]
        # 创建DataFrame
        df = pd.DataFrame(data, columns=['source_id', 'relationship_type', 'target_id'])
        # 导出为CSV
        df.to_csv('get_csv_data.csv', index=False)



def export_all_relationships_to_csv_relation():
    driver = GraphDatabase.driver(
        uri=os.environ["NEO4J_URI"],
        auth=(os.environ["NEO4J_USERNAME"], os.environ["NEO4J_PASSWORD"])
    )
    
    with driver.session() as session:
        # 查询所有关系数据
        result = session.run(
            """
            MATCH (n)-[r]->(neighbor)
            WHERE NOT type(r) = 'MENTIONS'
            RETURN n.id + ' - ' + type(r) + ' -> ' + neighbor.id AS relationship
            UNION
            MATCH (n)<-[r]-(neighbor)
            WHERE NOT type(r) = 'MENTIONS'
            RETURN neighbor.id + ' - ' + type(r) + ' -> ' + n.id AS relationship
            """
        )
        
        # 提取查询结果
        data = [record['relationship'] for record in result]
        
        # 创建DataFrame
        df = pd.DataFrame(data, columns=['relationship'])
        
        # 导出为CSV
        df.to_csv('get_relation_data.csv', index=False)
