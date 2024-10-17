from element.qinfanapi import create_llm,create_embeddings
from langchain_community.vectorstores.neo4j_vector import remove_lucene_chars
from langchain_community.graphs import Neo4jGraph
from langchain_community.vectorstores import Neo4jVector
graph = Neo4jGraph(url="bolt://localhost:7687", username="neo4j", password="12345678")

def prompt_query(query):
    llm = create_llm()
    prompt = (
        "任务：query特征提取,只要输出词语，不要输出任何其他信息。\n"
        "例子：\n"
        "输入：小红和小丽都是谁呀？\n"
        "输出：小红，小丽\n"
        "输入：我不管我要吃巧克力和香蕉\n"
        "输出：巧克力，香蕉\n"
        "输入：巴黎奥运金牌第一名\n"
        "输出：巴黎奥运会，金牌\n"
        "按照上述事实回答问题:\n"
        f"输入：{query}\n"
        "输出："
    )
    response = llm(prompt)
    # response_list = [response.strip()] if response else []
    return ','.join(response) if isinstance(response, list) else response.strip()


def generate_full_text_query(input: str) -> str:
    full_text_query = ""
    words = [el for el in remove_lucene_chars(input).split() if el]
    for word in words[:-1]:
        full_text_query += f" {word}~2 AND"
    full_text_query += f" {words[-1]}~2"
    return full_text_query.strip()


def generate_full_text_query(input: str) -> str:
    words = [el for el in remove_lucene_chars(input).split() if el]
    if not words:
        return ""
    full_text_query = " AND ".join([f"{word}~2" for word in words])
    print(f"Generated Query: {full_text_query}")
    return full_text_query.strip()

graph.query(
    "CREATE FULLTEXT INDEX entity IF NOT EXISTS FOR (e:__Entity__) ON EACH [e.id]")


def graph_retriever(question: str) -> str:
    """
    Collects the neighborhood of entities mentioned
    in the question
    """
    result = ""
    #prompt_query提取特征实体
    entities = prompt_query(question)
    for entity in entities:
        response = graph.query(
            """CALL db.index.fulltext.queryNodes('entity', $query, {limit:2})
            YIELD node,score
            CALL {
              WITH node
              MATCH (node)-[r:!MENTIONS]->(neighbor)
              RETURN node.id + ' - ' + type(r) + ' -> ' + neighbor.id AS output
              UNION ALL
              WITH node
              MATCH (node)<-[r:!MENTIONS]-(neighbor)
              RETURN neighbor.id + ' - ' + type(r) + ' -> ' +  node.id AS output
            }
            RETURN output LIMIT 50
            """,
            {"query": generate_full_text_query(entity)},
        )
        result += "\n".join([el['output'] for el in response])
    return result


vector_index = Neo4jVector.from_existing_graph(
    create_embeddings(),
    search_type="hybrid",
    node_label="Document",
    text_node_properties=["text"],
    embedding_node_property="embedding"
)
vector_retriever = vector_index.as_retriever()



def full_retriever(question: str):
    graph_data = graph_retriever(question)
    vector_data = [el.page_content for el in vector_retriever.invoke(question)]
    final_data = f"""Graph data:
{graph_data}
vector data:
{"#Document ". join(vector_data)}
    """
    print(final_data)
    return final_data


