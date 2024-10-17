import os
from neo4j import GraphDatabase

def clear_database(tx):
    """
    清除Neo4j数据库中的所有节点和关系。
    
    :param tx: 事务对象
    """
    # 删除所有关系
    tx.run("MATCH ()-[r]->() DELETE r")
    # 删除所有节点
    tx.run("MATCH (n) DELETE n")

def clear_neo4j_database(uri, username, password):
    """
    连接到Neo4j数据库并清除所有数据。
    
    :param uri: 数据库URI
    :param username: 数据库用户名
    :param password: 数据库密码
    """
    try:
        # 初始化驱动
        driver = GraphDatabase.driver(uri, auth=(username, password))
        
        with driver.session() as session:
            # 执行事务以清除数据库
            session.write_transaction(clear_database)
        
        print("数据库已成功清除。")
    except Exception as e:
        print(f"清除数据库时发生错误: {e}")
    finally:
        # 关闭驱动
        if 'driver' in locals():
            driver.close()


# clear_neo4j_database("bolt://localhost:7687", "neo4j", "your_password")