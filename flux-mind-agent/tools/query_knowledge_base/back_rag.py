import requests
import json
import numpy as np
import faiss
import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("SILICONFLOW_API_KEY", "")
EMBEDDING_MODEL = os.getenv("SILICONFLOW_EMBEDDING_MODEL", "Qwen/Qwen3-Embedding-8B")
EMBEDDING_BASE_URL = os.getenv("SILICONFLOW_BASE_URL", "https://api.siliconflow.cn/v1")

if not API_KEY:
    raise RuntimeError("SILICONFLOW_API_KEY is required. Set it in the environment or .env file.")

BASE_DIR = Path(__file__).resolve().parent
VECTOR_DIR = BASE_DIR / "tools" / "query_knowledge_base" / "knowledge"
FAISS_INDEX_PATH = VECTOR_DIR / "index.faiss"
META_PATH = VECTOR_DIR / "meta.json"

param_chunks = [
    "dc1（中心柱直径）：EC 型磁芯中心柱的直径，单位 mm。取值范围 5~30mm。dc1 越大，磁芯截面积越大，可承载的磁通量越大，有助于提高电感量和饱和电流，但体积和占地面积也会增大。",
    "dc2（外侧磁柱直径）：磁芯外侧柱体的直径，单位 mm。取值范围 1~10mm。dc2 影响磁芯整体结构的紧凑性与外侧磁通分布。",
    "ht（绕线窗口高度）：磁芯绕线区域的垂直高度，单位 mm。取值范围 1~10mm。ht 直接限制垂直方向可容纳的匝数，增加 ht 可以容纳更多匝数，但会增加器件总高度和体积。",
    "lg1（中心柱气隙长度）：磁芯中心柱的气隙长度，单位 mm。取值范围 0.1~4mm。lg1 是调节电感量和饱和电流的关键参数：lg1 增大→磁阻增大→电感量下降→饱和电流提高。",
    "lg2（外侧磁柱气隙长度）：磁芯外侧柱体的气隙长度，单位 mm。取值范围与 lg1 相同，为 0.1~4mm。lg2 用于平衡磁通分布，避免外侧磁柱局部饱和。",
    "Nx（水平方向匝数）：水平方向的线圈匝数或单元数量，取值 1~10 的整数。Nx 影响水平方向尺寸和总匝数。需满足约束条件 0.1 < Nx × c < 10。",
    "Ny（垂直方向匝数）：垂直方向的线圈匝数或单元数量，取值 1~10 的整数。Ny 影响垂直方向尺寸和总匝数。需满足约束条件 0.1 < Ny × c < 10。",
    "c（绕组间距）：相邻绕组之间的间距，单位 mm。取值范围 1~5mm。c 影响线圈之间的绝缘和散热。间距过小可能导致击穿风险，过大则降低窗口利用率，增加器件体积。",
    "f（工作频率）：电感的工作频率，单位 kHz。取值范围 100~500kHz。用户可指定精确值（如 f=200）或范围（如 f 在 100 到 300 之间）。频率越高，磁芯损耗越大，同时交流铜损因集肤效应也会增大。",
    "i（激励电流）：流过电感的电流，单位 A。取值范围 1~50A。用户可指定精确值（如 i=10）或范围（如 i 在 5 到 20 之间）。电流与磁通密度 B 成正比：B = μ₀×N×i / lg。当 B 超过材料饱和磁通密度 Bmax（约 0.3T）时，电感量会急剧下降。"
]

output_chunks = [
    "L（电感量）：单位 μH，由 ANN 代理模型预测。电感量由磁芯几何参数、匝数和气隙共同决定。总匝数 Nx×Ny 越大、气隙 lg1 越小，电感量越高。",
    "Pw（绕组铜损）：单位 W，由 ANN 代理模型预测。绕组铜损与匝数、电流、频率和导体尺寸有关。匝数越多、频率越高，铜损越大。",
    "Pc（磁芯损耗）：单位 W，由 ANN 代理模型预测。磁芯损耗主要由磁滞损耗和涡流损耗组成，与频率和磁通密度密切相关。",
    "P（总损耗）：P = Pw + Pc，单位 W。是优化的主要目标之一。在低频应用中铜损占主导，在高频应用中磁芯损耗占主导。",
    "V（体积）：由器件外形尺寸计算，V = 宽 × 长 × 高，单位 mm³。宽和长主要由 dc1、dc2、Nx、c 决定，高主要由 Ny、c、ht 决定。是优化的另一个主要目标。",
    "S（占地面积）：S = 宽 × 长，单位 mm²。反映器件在 PCB 上的占用面积。在空间受限的应用中，占地面积可能比体积更重要。"
]

relation_chunks = [
    "Nx 和 Ny 的乘积（Nx×Ny）决定线圈总匝数。总匝数越大，电感量越高，但铜损和器件体积也随之增加。需要在电感量需求和损耗、体积之间取得平衡。",
    "dc1 和 dc2 共同决定磁芯的径向尺寸。dc1 为中心柱直径，dc2 为外侧磁柱直径，两者配合决定绕线窗口宽度和磁芯整体外径。",
    "c（绕组间距）同时影响水平和垂直方向的尺寸，因为器件宽度包含 Nx×c 项，高度包含 Ny×c 项。减小 c 可以缩小体积，但需注意绝缘要求。",
    "气隙 lg1 与电感量和饱和电流存在反向关系：增大 lg1 会降低电感量但提高饱和电流能力。lg2 用于平衡外侧磁柱的磁通分布，通常与 lg1 配合设计。"
]

guidance_chunks = [
    "如果目标是低损耗：可以减小总匝数（降低 Nx 或 Ny）以降低铜损，同时适当增大 c 以改善散热和降低邻近效应。代价是电感量会降低、需要更大的气隙补偿。",
    "如果目标是小体积：可以减小 dc1（缩小磁芯截面）、减小 c（缩小间距）、适当减少 Nx 和 Ny。代价是电感量降低、损耗密度增大。",
    "如果目标是紧凑占地面积：可以减小 dc1 和 Nx 以缩小水平尺寸，用增加 Ny（增加高度方向匝数）来补偿电感量。代价是器件变高。",
    "电感设计的核心权衡是损耗、体积和电感量的三角关系：提高电感量通常需要更多匝数或更大磁芯，这会导致体积和损耗增加。优化就是在这三者之间找到最合适的平衡。"
]

scenario_chunks = [
    "DC-DC Buck 降压变换器输出滤波电感：典型工作频率 100~500kHz，电流中等。参数建议：dc1 取 6~8mm 以平衡磁芯截面与体积；Nx=3~5、Ny=3~5 提供足够匝数获取目标电感量；c 取 1.5~2.5mm 兼顾绝缘和紧凑；优化时建议偏好'均衡'或'低损耗'。",
    "DC-DC Boost 升压变换器电感：输入电流较大，需要较高的饱和电流能力。参数建议：dc1 取 7~10mm 以增大磁芯截面承载更多磁通；Nx 和 Ny 不宜过大（各取 2~4），避免铜损过高；c 取 2~3mm 改善散热；优化时建议偏好'低损耗'，因为升压电感持续通过大电流。",
    "大电流低压应用（如 VRM/CPU 供电模块）：特点是电流大（>10A）、电感量需求小、体积要求严格。参数建议：dc1 取 8~10mm 提供大截面防饱和；Nx 和 Ny 取较小值（各 1~3），匝数少以降低铜损和获得小电感量；c 取 2~3mm 保证大电流下的散热；优化时建议偏好'紧凑'或'小体积'。",
    "小功率高频应用（如 LED 驱动电源）：特点是电流小、频率高（200kHz 以上）、体积优先。参数建议：dc1 取 5~7mm 即可满足小电流需求；Nx=2~4、Ny=2~4 提供适当匝数；c 取 1~2mm 以缩小体积；优化时建议偏好'小体积'或'紧凑'，因为 LED 驱动通常空间受限。",
    "车载充电器（OBC）电感：工作频率通常 100~300kHz，电流较大，对效率和体积都有严格要求。参数建议：dc1 取 8~10mm 保证大电流下不饱和；Nx=3~5、Ny=3~5 获取足够电感量；c 取 2~3mm 兼顾绝缘和散热（车载环境温度高）；优化时建议先用'均衡'模式查看全局权衡，再根据具体需求用'低损耗'或'小体积'偏好筛选。"
]

system_chunks = [
    "本系统使用离线训练的 ANN 代理模型（神经网络）代替有限元仿真，可以快速预测给定参数组合下的电感量 L、绕组损耗 Pw 和磁芯损耗 Pc。",
    "优化过程：系统先根据用户指定的参数过滤设计空间，然后用 ANN 模型对所有候选方案进行批量预测，计算体积 V、面积 S 和总损耗 P，最后用 ε-Pareto 方法筛选出非劣解。",
    "系统从 Pareto 前沿中选出 5 类代表方案：最低损耗（Lowest Loss）、最小体积（Smallest Volume）、均衡方案（Balanced）、最高效率（High Efficiency）、最紧凑（Compact）。",
    "偏好重排功能：用户可以用自然语言表达偏好（如'优先体积小'或'优先低损耗'），系统会按偏好加权重新排序候选方案。偏好强度分为 light、medium、strong 三档。"
]

ALL_CHUNKS = param_chunks + output_chunks + relation_chunks + guidance_chunks + scenario_chunks + system_chunks

def embed_text(text: str) -> np.ndarray:
    url = f"{EMBEDDING_BASE_URL.rstrip('/')}/embeddings"
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": EMBEDDING_MODEL,
        "input": text
    }

    resp = requests.post(url, json=payload, headers=headers)
    resp.raise_for_status()

    embedding = resp.json()["data"][0]["embedding"]
    return np.array(embedding, dtype=np.float32)

def build_faiss_index(chunks):
    VECTOR_DIR.mkdir(parents=True, exist_ok=True)

    vectors = []
    for text in chunks:
        vec = embed_text(text)
        vectors.append(vec)

    vectors = np.vstack(vectors)
    dim = vectors.shape[1]

    # 使用内积，相当于 cosine similarity（前提是向量归一化）
    faiss.normalize_L2(vectors)
    index = faiss.IndexFlatIP(dim)
    index.add(vectors)

    faiss.write_index(index, str(FAISS_INDEX_PATH))

    with META_PATH.open("w", encoding="utf-8") as f:
        json.dump(chunks, f, ensure_ascii=False, indent=2)

    print(f"FAISS index saved: {FAISS_INDEX_PATH}")
    print(f"Metadata saved: {META_PATH}")

def retrieve_from_faiss(query: str, top_k: int = 3):
    index = faiss.read_index(str(FAISS_INDEX_PATH))

    with META_PATH.open("r", encoding="utf-8") as f:
        texts = json.load(f)

    query_vec = embed_text(query).reshape(1, -1)
    faiss.normalize_L2(query_vec)

    scores, indices = index.search(query_vec, top_k)

    results = []
    for score, idx in zip(scores[0], indices[0]):
        results.append({
            "score": float(score),
            "text": texts[idx]
        })

    return results

if __name__ == "__main__":
    print(f"知识库片段总数: {len(ALL_CHUNKS)}")
    print("正在重建 FAISS 索引...")
    build_faiss_index(ALL_CHUNKS)
    print("索引构建完成。\n")

    # 测试检索
    query = "ht 在电感设计中的定义与作用"
    results = retrieve_from_faiss(query, top_k=3)

    print(f"查询: {query}")
    for r in results:
        print(f"[{r['score']:.3f}] {r['text']}")
