# 🧬 13 Apostles: Autonomous Multi-Agent Code Evolution Framework

> **서로 다른 인지적 편향을 지닌 13인의 AI 사도가 이끄는 지향성 돌연변이 & 다차원 합의 선택 기반의 자율 코드 진화 엔진**
> 
> *An autonomous, self-modifying evolution engine that adapts Python programs under strict multi-dimensional selection pressures, validated on an empirical dataset of **153 unique compile-ready organisms** across 7 generations.*

---

## 🗺️ 1. 한눈에 보는 시스템 도식 (System Schematic)

본 프레임워크는 기존 유전 프로그래밍(GP)의 한계인 **구문 붕괴(Lethal Mutation)**를 LLM의 코드 이해도를 바탕으로 극복하고, 다중 에이전트의 합의 투표와 면역 시스템(Veto)을 결합하여 코드의 안전하고 우상향하는 진화를 이끌어냅니다.

```mermaid
flowchart TD
    classDef parent fill:#f9f,stroke:#333,stroke-width:2px;
    classDef apostle fill:#bbf,stroke:#333,stroke-width:1px;
    classDef filter fill:#ff9,stroke:#333,stroke-width:1px;
    classDef success fill:#9f9,stroke:#333,stroke-width:2px;
    classDef fail fill:#f99,stroke:#333,stroke-width:1px;

    Parent["🧬 부모 코드 (Parent Genotype) <br> e.g., 0.py"]:::parent --> MutationEngine["⚙️ Directed Mutation Engine"]

    subgraph Apostles ["13인의 사도 (Apostles Personas)"]
        A1["Melchior <br> (극한 최적화)"]:::apostle
        A2["Balthasar <br> (안전 & 가독성)"]:::apostle
        A3["Casper <br> (기발한 돌발변칙)"]:::apostle
        A_More["... 10 More Personas"]:::apostle
    end

    MutationEngine --> Apostles
    Apostles -->|고유 인지 편향 기반 변이 제안| Candidates["📦 후보군 생성 (Candidate Genotypes)"]

    Candidates --> Filter1{"1차: 구문 검증 <br> (Syntax Check)"}:::filter
    Filter1 -->|Syntax Error| Dead1["💀 치사 도태 (Lethal Mutation)"]:::fail
    
    Filter1 -->|Pass| Filter2{"2차: 5초 성능 측정 <br> (Ecological Benchmark)"}:::filter
    Filter2 -->|Timeout / Fail| Dead2["💀 환경적 도태 (Timeout)"]:::fail
    
    Filter2 -->|Pass| Filter3{"3차: 다차원 합의 투표 <br> (Consensus & Veto)"}:::filter
    Filter3 -->|거부권 (Veto) 발동| Dead3["🛡️ 면역 도태 (Vetoed)"]:::fail
    
    Filter3 -->|합의 통과 (Consent)| Success["🏆 우량종 최종 보존 <br> e.g., 04.py"]:::success

    Success -->|다음 세대의 조상으로 채택| Parent
```

### ⚡ 핵심 지표 요약 (Key Statistics at a Glance)
153개 개체군의 전수 조사를 통해 디지털 공간에서 생물학적 진화 법칙이 그대로 재현됨이 입증되었습니다.
*   **유전적 부동 (Genetic Drift)**: `04` 계통(소수 체 & 실시간 루프 가드 탑재)이 **생태계의 96.7%(148/153)**를 독점 식민지화.
*   **수렴 진화 (Convergent Evolution)**: 서로 다른 가문에서 기원한 종들이 극한 환경에서 **"C-GCD Vector Sieve"**와 **"Predictive Time Guard"** 아키텍처로 독립적 코딩 수렴.
*   **안정적 진화 평형 (Speciation)**: 가파르게 비트를 곱해 나가는 **지수형 아종(51.9%)**과 남은 시간에 맞춰 정교하게 성장 비트를 미세 조정하는 **적응형 아종(45.5%)**의 평형 공존.
*   **면역 체계 (Veto System)**: 신뢰성을 해치고 속도만 올리는 치팅 제안(**Fermat Gambit**, 50%) 등 **총 28회의 파괴적 변이를 성공적으로 완벽 차단**.

---

## 2. 실증 연구 요약: 153개 개체군 전수 분석

본 프로젝트는 단순한 코드 튜닝 프레임워크가 아닌, 자율 진화형 소프트웨어의 이론적 토대를 마련하기 위한 실증적 연구체입니다. 5초 제한시간 내 거대 소수 탐색 미션을 기반으로 수행된 세대별 핵심 지표는 다음과 같습니다.

### 📊 세대별 개체군 추이
| 진화 세대 (Gen) | 생존 개체 수 | 평균 라인 수 | 평균 부모 유사도 | 지배적 후보 필터 (Dominant Sieve) |
| :---: | :---: | :---: | :---: | :---: |
| **Gen 0** | 1 | 232.0 | - | Basic random.getrandbits (100%) |
| **Gen 1** | 3 | 172.7 | 50.6% | Sieve pre-filtering (33.3%) |
| **Gen 2** | 4 | 197.3 | 82.5% | Sieve pre-filtering (75.0%) |
| **Gen 3** | 5 | 142.2 | 76.2% | Sieve pre-filtering (100.0%) |
| **Gen 4** | 9 | 145.8 | 70.2% | Sieve pre-filtering (88.9%) |
| **Gen 5** | 19 | 137.7 | 78.1% | Sieve pre-filtering (100.0%) |
| **Gen 6** | 35 | 148.5 | 77.6% | Sieve pre-filtering (94.3%) |
| **Gen 7** | 77 | 153.1 | 79.8% | Sieve pre-filtering (92.2%) |

> [!TIP]
> **유전적 유사도의 황금률 (Golden Ratio of Mutation)**:
> 살아남은 개체들의 부모 대비 코드 유사도는 **평균 77.2%** 선으로 수렴합니다. 이는 코드 문법을 파괴하지 않으면서 최적화를 극대화하는 가장 완벽한 변이율이 **20~23% 범위**에 있음을 뜻합니다.

---

## 3. 핵심 기능 (Key Features)

### 1. 🧬 다중 에이전트 지향성 돌연변이 (13 Apostles)
*   Melchior(성능), Balthasar(안전/가독성), Casper(변칙 알고리즘) 등 13인의 독자적인 성격과 가중치를 부여받은 AI가 부모 코드를 세밀하게 분석하고 변이 코드를 작성합니다.

### 2. ♻️ 점진적 진화 & 캐싱 지원 (Incremental Evolution)
*   이전에 수행한 진화 기록을 워크스페이스에서 자동으로 감지합니다. 동일 노드에 대해 진화를 다시 요청할 때, 이미 생성된 파일이 존재할 경우 **LLM API 호출을 즉시 건너뛰고 캐싱된 코드 데이터를 재사용**합니다. 
*   추가적인 진화 세대를 요구하는 경우에만 차이만큼의 노드를 신규 생성하여 비용과 속도를 극대화합니다.

### 3. 🧪 Evolutionary Diversity Analyzer (🧬 다양성 분석 패널)
*   Streamlit 대시보드 하단에서 제공되는 양방향 분석 패널입니다.
*   **코드 유사성 (Code Similarity)**: 선택한 2~5개 노드 간의 AST 및 텍스트 구조를 pairwise 비교합니다.
*   **결과 유사성 (Output Similarity)**: 5초의 타임아웃 제한 내에서 선택된 프로그램들을 직접 서브프로세스로 구동하여, 표준 출력(stdout)의 기능적 싱크율을 대조합니다.
*   이를 통해 진화가 **동일 결과로 수렴(Convergence)** 중인지, 새로운 구조와 행동으로 **발산(Divergence)** 중인지 직관적으로 진단합니다.

---

## 4. 시작하기 (Quick Start)

### A. 의존성 설치
```bash
pip install -r requirements.txt
```

### B. Gemini API Key 등록
프로젝트 진화를 지휘하는 사도들의 연산 자원을 위해 Google Gemini API Key가 필요합니다.
```powershell
# Windows PowerShell
$env:GEMINI_API_KEY="your_actual_api_key_here"

# Linux / macOS
export GEMINI_API_KEY="your_actual_api_key_here"
```

### C. 인터랙티브 대시보드 실행 (Streamlit UI)
시각적인 진화 트리와 Lineage 이력, 다양성 분석 패널을 한눈에 보며 실행할 수 있습니다.
```bash
streamlit run app.py
```

### D. 터미널 명령으로 직접 실행
```bash
# 0.py를 조상으로 삼아 3개의 자식 노드를 분기 진화시킵니다.
python evolution.py 0.py --children 3
```

---

## 5. 학술 연구 및 심층 분석 보고서
본 프레임워크의 상세 통계적 지표와 수학적 분석 결과는 아래 독립 아티팩트에 피어 리뷰 수준의 논문 형식으로 수록되어 있습니다.
*   **심층 진화 분석 논문 전문**: [scientific_analysis.md](file:///C:/Users/eljja/.gemini/antigravity/brain/996e21c3-f9ac-4ef8-80c5-6e25c53f4011/scientific_analysis.md)
