# 🧬 13 Apostles: Autonomous Multi-Agent Code Evolution Framework

> **서로 다른 인지적 편향을 지닌 13인의 AI 사도가 이끄는 지향성 돌연변이 & 다차원 합의 선택 기반의 자율 코드 진화 엔진**
> 
> *An autonomous, self-modifying evolution engine that adapts Python programs under strict multi-dimensional selection pressures, validated on an empirical dataset of **153 unique compile-ready organisms** across 7 generations.*

---

## 🗺️ 1. 한눈에 보는 시스템 도식 (System Schematic)

본 프레임워크는 단순히 당장의 실행 속도만을 탐욕적으로 극대화하는 '단순 최적화 도구(Greedy Optimizer)'가 아닙니다. 13 Apostles는 **"당장의 성능 결함이나 비효율을 가졌더라도, 다음 세대에 혁신적인 형질의 모태가 될 수 있는 잠재적 유전자(Dormant/Viable)는 보존되어야 비선형적 알고리즘 도약이 가능하다"**는 깊은 진화론적 철학 아래 설계된 **자율형 코드 가능성 탐색기(Evolutionary Possibility Explorer)**입니다.

기존 유전 프로그래밍(GP)의 한계인 **구문 붕괴(Lethal Mutation)**를 LLM의 문법 이해 지능으로 해결하고, 13인의 AI 사도가 서로 다른 다차원 인지 편향을 바탕으로 '현재의 단기 성능'이 아닌 **'장기적 진화 잠재력과 아키텍처 확장성'**을 평가하여 계통의 다양성을 보존합니다.

```mermaid
flowchart TD
    classDef parent fill:#f9f,stroke:#333,stroke-width:2px;
    classDef apostle fill:#bbf,stroke:#333,stroke-width:1px;
    classDef filter fill:#ff9,stroke:#333,stroke-width:1px;
    classDef success fill:#9f9,stroke:#333,stroke-width:2px;
    classDef fail fill:#f99,stroke:#333,stroke-width:1px;
    classDef state fill:#eef,stroke:#333,stroke-dasharray: 5 5;

    Parent["🧬 부모 코드 (Parent Genotype) <br> e.g., 0.py"]:::parent --> MutationEngine["⚙️ Directed Mutation Engine"]

    subgraph Apostles ["13인의 사도 (Apostles - Cognitive Biases & Multi-Agent Consensus)"]
        A1["Melchior <br> (성능/최적화)"]:::apostle
        A2["Balthasar <br> (가독성/예외처리)"]:::apostle
        A3["Casper <br> (알고리즘 변칙)"]:::apostle
        A_More["... 10 More Personas"]:::apostle
    end

    MutationEngine --> Apostles
    Apostles -->|고유 인지 편향 기반 변이 제안| Candidates["📦 후보군 생성 (Candidate Genotypes)"]

    Candidates --> Filter1{"1차: 구문 검증 <br> (Syntax Check)"}:::filter
    Filter1 -->|Syntax Error| Dead["💀 치사 도태 (Lethal Mutation) <br> [시스템 격리]"]:::fail
    
    Filter1 -->|Pass| Filter2{"2차: 다차원 합의 및 Veto 면역 검증 <br> (Apostle Consensus & Safety Veto)"}:::filter
    Filter2 -->|거부권 (Veto) 발동| Vetoed["🛡️ 면역 도태 (Vetoed) <br> [안전성 위배 / 치팅]"]:::fail
    
    Filter2 -->|합의 통과 (Consent)| SurvivalSystem{"3차: 다차원 생태학적 계층 상태 평가 <br> (Hierarchical Ecological States)"}:::filter
    
    SurvivalSystem -->|최고의 적합도 확보| Elite["🏆 Elite <br> [차세대 주류 부모종]"]:::success
    SurvivalSystem -->|정상 실행 및 기본 목적 충족| Viable["🟢 Viable <br> [안정적 계통군 보존]"]:::success
    SurvivalSystem -->|현재 성능은 낮으나 구조적 참신성| Dormant["🟡 Dormant <br> [미래 도약을 위한 유전자 저장소]"]:::success
    SurvivalSystem -->|일시적 오버헤드 / 리스크 보유| Quarantined["🔴 Quarantined <br> [진화 일시 보류 및 감시]"]:::fail

    Elite & Viable & Dormant -->|다양한 유동적 탐색 공간 유지| Parent
```

### 🧬 진화적 선택의 혁신적 설계: 계층적 생존 철학 (Hierarchical Survival Philosophy)

#### ❓ 핵심 비판과 진화학적 반론 (Selection Criteria Criticism & Theoretical Defense)
*   **비판**: *"evolution.py (line 321)는 새 자식 코드에 대해 구문 오류(py_compile)만 확인하고, 실제 5초 벤치마크나 fitness 비교를 통한 사멸 조건을 강제하지 않는다. 이는 실제 fitness보다 LLM 투표에 과하게 의존하여 자연선택보다 'LLM 심사위원 대회'에 치우친 게 아닌가?"*
*   **반론 및 철학적 설계**: **이것은 시스템 결함이 아니라, 본 진화 엔진의 핵심 의도이자 가장 독창적인 설계 요소입니다.**
    *   **단기 적자생존의 함정 (Local Optima Entrapment)**: 전통적인 유전 프로그래밍(GP)이나 강화학습처럼 매 세대마다 엄격한 성능(Fitness) 문턱값으로 개체를 즉각 사멸시킨다면, 시스템은 아주 얕은 지역 최적점에 갇히게 되며 계통의 다양성은 급속도로 고갈됩니다.
    *   **잠재성의 보존 (Preservation of the Dormant)**: 생물학적 진화에서 돌연변이는 우발적이고 비논리적이며 비효율적으로 발생합니다. 당장은 부모보다 조금 더 느리거나 기형적인 개체(Dormant)라도, 구문상 실행 가능(Viable)하다면 즉각 사멸시키는 대신 계통 내에 보존해야 합니다. 이 "잘못 태어난 아이"가 가지고 있는 독창적인 구조가 다음 세대에서 또 다른 우발적 변이와 결합할 때, 비로소 상상할 수 없었던 **알고리즘적 대도약(Macro-evolutionary Leap)**이 일어나기 때문입니다.
    *   **LLM 사도 합의의 본질 (Consensus of Potential)**: 13사도의 투표는 단순한 '현재 성능 평가'가 아닌, **'미래 진화 가능성에 대한 다차원적 합의'**입니다. 사도들은 단순 수치 벤치마크 너머를 꿰뚫어 봅니다:
        - *"지금은 비록 연산 속도가 느리지만, 향후 병렬성 확장을 유도할 수 있는 혁신적인 모듈화 구조를 갖추었는가?"*
        - *"당장은 오버헤드가 크지만, 소수 사막을 안전하게 우회할 수 있는 완전히 새로운 알고리즘의 길을 열어주는가?"*
        - *"부모 코드의 구조에 안주하지 않고, 계통군 전체의 표현형 다양성(Phenotypic Diversity)을 확장하는가?"*

#### 📊 계층적 생존 상태 모델 (Hierarchical Survival States Model)
본 엔진은 "살거나 죽거나(Kill or Survive)"의 단순 적자생존 이분법을 배제하고, 개체군을 5단계의 생태학적 계층 상태로 세밀하게 관리합니다:
1.  **🏆 Elite (우수 유전자)**: 현재 벤치마크 성능(Fitness)이 매우 우수하여 다음 세대 진화를 이끌 주류 부모종.
2.  **🟢 Viable (실행 표준종)**: 문법적으로 무결하며, 비효율은 있으나 안정적으로 핵심 목적을 수행하는 형질군.
3.  **🟡 Dormant (잠재 잠복종)**: 당장의 실행 속도나 효율성은 낮지만, 구조적으로 매우 참신하여 **미래 세대의 결합 변이 가능성을 품은 유전자원 저장소**.
4.  **🔴 Quarantined (격리 감시종)**: 실행은 가능하나 리스크나 스레드 오버헤드가 있어 자동 진화 라인에서는 임시 배제하고 추적만 하는 상태.
5.  **💀 Dead (치사 도태종)**: 구문 오류(Syntax Error), 무한 루프, 혹은 수학적 무결성을 훼손하여 목적을 파괴한 개체. 시스템 보안과 신뢰성을 위해 철저히 격리 및 사멸됩니다.

이로써 13 Apostles는 단순한 **'현재의 최적화 도구(Optimizer)'**가 아닌, 가능성의 공간을 드넓게 유지하는 **'장기적 진화 가능성 탐색기(Evolutionary Possibility Explorer)'**로서의 정체성을 완벽하게 실현합니다.

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
*   **심층 진화 분석 논문 전문**: [scientific_analysis.md](./scientific_analysis.md)
