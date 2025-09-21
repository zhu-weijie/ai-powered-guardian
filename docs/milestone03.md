#### Web-facing UI & API Gateway

*   **Problem:** The system requires a secure, managed entry point for external API calls and a user interface for administrators. Direct exposure of the RBAC service is not secure or scalable.
*   **Solution:** Introduce an **API Gateway** to handle all incoming traffic, providing routing, rate limiting, and a single point of security enforcement. Add a containerized **Web UI** service (e.g., a React application) served via a **CloudFront CDN** for performance and low latency. The RBAC service will be moved to a private subnet, accessible only through the API Gateway.
*   **Trade-offs:** This adds several new components, increasing complexity. However, it is a non-negotiable step for a production system, providing massive benefits in security (by hiding backend services), scalability, and manageability. The CDN adds cost but is essential for a good global user experience.

#### 1. Logical View (C4 Component Diagram)

This view introduces the new `Web UI` component and shows how users now interact with the system indirectly through the `API Gateway`.

```mermaid
graph TD
    subgraph SystemBoundary ["System Boundary"]
        WebUI["Web UI (SPA)"]
        APIGateway[API Gateway]
        RBAC_Service["RBAC Service (Container)"]
        
        subgraph DataStores ["Data Stores"]
            DB[(Relational DB)]
            Cache[(Session/Cache Store)]
        end
    end

    User[Administrator] -->|Uses Browser| WebUI
    WebUI -->|Makes API Calls| APIGateway
    
    APIGateway -->|Forwards Requests| RBAC_Service

    RBAC_Service -->|Reads/Writes| DB
    RBAC_Service -->|Reads/Writes| Cache

    style SystemBoundary fill:#f4f4f4,stroke:#333,stroke-width:2px
```

#### 2. Physical View (AWS Deployment Diagram)

This is a significant evolution. The `RBAC Service` is moved to a private subnet. The `API Gateway` becomes the public-facing entry point, and a new `CloudFront` + `S3` combination is added to serve the UI.

```mermaid
graph TD
    subgraph AWS_Cloud ["AWS Cloud"]
        subgraph Global_Services ["Global Services"]
            CloudFront[("AWS CloudFront (CDN)")]
            S3[("AWS S3 Bucket")]
        end

        subgraph VPC ["VPC"]
            subgraph Public_Subnet ["Public Subnet"]
                APIGW[("AWS API Gateway")]
            end
            
            subgraph Private_Subnet_C ["Private Subnet C (Compute)"]
                 Fargate[("AWS Fargate")]
            end

            subgraph Private_Subnet_A ["Private Subnet A (Data)"]
                RDS[("AWS RDS for PostgreSQL")]
            end

            subgraph Private_Subnet_B ["Private Subnet B (Data)"]
                ElastiCache[("AWS ElastiCache for Redis")]
            end
        end
    end
    
    subgraph Container_Def ["Container Definition"]
        WebUI_Container[("Container: Web UI (React)")]
        RBAC_Container[("Container: RBAC Service")]
    end

    User[Administrator] -->|HTTPS| CloudFront
    CloudFront -->|Serves Static Content| S3
    User -->|API Calls via Browser| APIGW
    
    S3 -- Deploys --> WebUI_Container

    APIGW -->|Invokes via VPC Link| Fargate
    
    Fargate -- Deploys --> RBAC_Container

    RBAC_Container -->|Internal VPC Routing| RDS
    RBAC_Container -->|Internal VPC Routing| ElastiCache

    style AWS_Cloud fill:#FFDAB9,stroke:#333,stroke-width:2px
    style Global_Services fill:#D1E8E2,stroke:#333,stroke-width:2px
```

#### 3. Component-to-Resource Mapping Table

| Logical Component | Physical Resource | Rationale for Choice |
| :--- | :--- | :--- |
| **Web UI** | **AWS S3 + AWS CloudFront** | **Performance & Scalability:** S3 provides durable, cheap object storage for the static UI assets (HTML, CSS, JS). CloudFront is a global CDN that caches these assets at edge locations, providing low-latency access for users worldwide. |
| **API Gateway** | **AWS API Gateway (HTTP API)** | **Security & Management:** Provides a secure, managed entry point. It handles authentication, rate limiting, and request validation before traffic ever reaches our backend. The HTTP API type is cost-effective and suitable for our REST/gRPC needs. |
| **RBAC Service** | **AWS Fargate Task (in Private Subnet)** | **Security & Serverless:** Fargate remains ideal for its serverless nature. Moving it to a **private subnet** is a critical security enhancement. It is no longer directly accessible from the internet. |
| **Relational DB** | **AWS RDS for PostgreSQL** | **Managed & Reliable:** No change in rationale. |
| **Session/Cache Store** | **AWS ElastiCache for Redis** | **Managed & High-Performance:** No change in rationale. |
