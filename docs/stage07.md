#### Caching for Performance

*   **Problem:** The real-time access decision path now involves multiple network calls (to the AI service and the database). As system load increases, this could lead to unacceptable latency, violating our performance NFRs.
*   **Solution:** Implement a caching strategy using our existing Redis component. The RBAC Service will cache two key pieces of data for a short Time-to-Live (TTL):
    1.  **Resolved Permissions:** The final set of permissions for a user, to avoid repeated database joins.
    2.  **AI Risk Scores:** The risk score for a specific user/asset combination, to avoid re-calculating it on every single request.
*   **Trade-offs:** This introduces eventual consistency. A change in a user's permissions might not be reflected until the cache expires (a delay of a few seconds to minutes). This is a standard and generally acceptable trade-off for the significant performance gain. The logic within the RBAC service becomes more complex as it must now manage cache-miss and cache-hit scenarios.

#### 1. Logical View (C4 Component Diagram)

This view explicitly shows the new caching logic within the `RBAC Service`'s workflow.

```mermaid
graph TD
    subgraph SystemBoundary ["System Boundary"]
        subgraph RBAC_Service ["RBAC Service"]
            direction LR
            A("1.Check Cache for Permissions/Score")
            B("2.On Cache Miss")
            C("3a.Get Permissions from DB")
            D("3b.Get Score from AI Service")
            E("4.Populate Cache")
            F("5.Make Final Decision")
        end

        AI_Service[AI Anomaly Detection Service]

        subgraph DataStores ["Data Stores"]
            AppDB[(Application DB)]
            Cache[(Performance & Session Cache)]
        end
    end

    User[User] --> |API Call| A

    A -- "Reads from" --> Cache
    A -- "Cache Miss" --> B
    B --> C & D
    C --> AppDB
    D --> AI_Service
    AppDB -- "Data" --> E
    AI_Service -- "Score" --> E
    E -- "Writes to" --> Cache
    A -- "Cache Hit" --> F
    E --> F
```

#### 2. Physical View (AWS Deployment Diagram)

This view re-introduces the `AWS ElastiCache for Redis` cluster from our earlier `data-persistence` step and shows the `RBAC Service` now actively communicating with it as part of the real-time flow.

```mermaid
graph TD
    subgraph AWS_Cloud ["AWS Cloud"]
        subgraph VPC ["VPC"]
            subgraph Public_Subnet ["Public Subnet"]
                APIGW[("AWS API Gateway")]
            end
            
            subgraph Private_Subnet_Compute ["Private Subnet (Compute)"]
                 RBAC_Fargate[("AWS Fargate: RBAC Service")]
            end

            subgraph Private_Subnet_Data ["Private Subnet (Data)"]
                App_RDS[("AWS RDS: App DB")]
                Redis[("AWS ElastiCache for Redis")]
            end
            
            subgraph Private_Subnet_Endpoints ["Private Subnet (Endpoints)"]
                SageMakerEndpoint[("SageMaker VPC Endpoint")]
            end
        end
        
        subgraph AWS_Managed_Services ["AWS Managed Services"]
             SageMaker[("Amazon SageMaker")]
        end
    end

    APIGW -- "Invokes via VPC Link" --> RBAC_Fargate
    
    RBAC_Fargate -- "Reads/Writes Cache" --> Redis
    RBAC_Fargate -- "On Cache Miss, Reads DB" --> App_RDS
    RBAC_Fargate -- "On Cache Miss, Invokes Model" --> SageMakerEndpoint
    SageMakerEndpoint --> SageMaker
    
    style AWS_Cloud fill:#FFDAB9,stroke:#333,stroke-width:2px
```

#### 3. Component-to-Resource Mapping Table

| Logical Component | Physical Resource | Rationale for Choice |
| :--- | :--- | :--- |
| **RBAC Service** | **AWS Fargate Task** | No change in rationale. |
| **AI Anomaly Detection Service**| **Amazon SageMaker** | No change in rationale. |
| **Performance & Session Cache**| **AWS ElastiCache for Redis** | **High-Speed & In-Memory:** Redis is an in-memory key-value store, providing microsecond latency for reads and writes, making it the perfect choice for a performance-critical cache. ElastiCache manages the deployment, scaling, and patching of the Redis cluster. |
| **Application DB** | **AWS RDS for PostgreSQL** | No change in rationale. |
