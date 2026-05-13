```mermaid
flowchart TD

    A([Start]) --> B[Initialize MASState<br/>with user_input and history]

    B --> C[IntentAgent<br/>Analyze user intent]

    C --> D[ClarificationAgent<br/>Check missing information]

    D --> E{Need clarification?}

    E -->|Yes| F[Return clarification question]
    F --> Z([End])

    E -->|No| G{Intent = adjust difficulty?}

    G -->|Yes| H[Retrieve previous summary]

    H --> I{Difficulty Action}

    I -->|Decrease| J[ReadabilityController<br/>simplify summary]

    I -->|Increase| K[ReadabilityController<br/>increase complexity]

    J --> L[Return adjusted summary]
    K --> L

    L --> Z

    G -->|No| M[PlanningAgent<br/>Generate execution plan]

    M --> N{Input contains image?}

    N -->|Yes| O[Image2TextAgent<br/>Extract OCR text]

    O --> P{OCR only task?}

    P -->|Yes| Q[Return OCR text]
    Q --> Z

    P -->|No| R[Set document = extracted text]

    N -->|No| S[Set document = user input]

    R --> T{Summarization Strategy}

    S --> T

    T -->|Extractive| U[ExtractorAgent (VES)]

    T -->|Abstractive| V[AbstracterAgent (VAS)]

    U --> W[EvaluationAgent<br/>Evaluate quality and readability]

    V --> W

    W --> X{Need improvement?}

    X -->|Yes| Y[PlanningAgent.refine(plan)]
    Y --> T

    X -->|No| AA[Store conversation and trace into memory]

    AA --> AB[Return final response<br/>summary + evaluation]

    AB --> Z([End])