#### Secrets Management & Security Hardening

*   **Problem:** Secrets such as database credentials, API keys, and service-to-service tokens are often managed through environment variables or configuration files. This is a significant security risk, as these secrets can be accidentally logged, checked into version control, or exposed if a container is compromised.
*   **Solution:** Integrate a dedicated, centralized secrets management service. All application services (RBAC, Audit, etc.) will be modified to fetch their required secrets from this vault at runtime using their IAM role for authentication. This removes all secrets from the application's configuration and code.
*   **Trade-offs:** This introduces a new dependency on the secrets management service. The application's startup time will be slightly longer as it needs to make an initial call to fetch its secrets. This also requires more rigorous IAM policy management. However, the immense security benefit of centralizing and securing secrets is a non-negotiable best practice for any production system.

#### 1. Logical View (C4 Component Diagram)

This view shows that before accessing a protected resource, our services must first retrieve the necessary credentials from a central `Secrets Vault`.

```mermaid
graph TD
    subgraph SystemBoundary ["System Boundary"]
        SecretsVault[Secrets Vault]
        Services["Application Services <br/> (RBAC, Audit, etc.)"]
        ProtectedResource[(Protected Resource <br/> e.g., Database)]
    end

    Services -- "1.Fetches credentials from" --> SecretsVault
    Services -- "2.Uses credentials to connect to" --> ProtectedResource
```

#### 2. Physical View (AWS Deployment Diagram)

This view introduces **AWS Secrets Manager** and a **VPC Endpoint** for it. It shows how our Fargate services, using their assigned IAM roles, will call the Secrets Manager endpoint to retrieve database credentials before connecting to RDS.

```mermaid
graph TD
    subgraph AWS_Cloud ["AWS Cloud"]
        subgraph VPC ["VPC"]
            subgraph Private_Compute ["Private Subnets (Compute)"]
                 Fargate_Service[("Fargate Service <br/> (e.g., RBAC Service)")]
            end

            subgraph Private_Data ["Private Subnets (Data)"]
                App_RDS[("AWS RDS: App DB")]
            end
            
            subgraph Private_Endpoints ["Private Subnets (Endpoints)"]
                SecretsManager_Endpoint[("Secrets Manager VPC Endpoint")]
            end
        end
        
        subgraph AWS_Managed_Services ["AWS Managed Services"]
             SecretsManager[("AWS Secrets Manager")]
        end
    end

    subgraph IAM_Role ["IAM Task Role"]
    end
    
    Fargate_Service -- "Assumes" --> IAM_Role
    
    IAM_Role -- "Grants permission for" --> Fargate_Service
    
    Fargate_Service -- "1.Calls 'GetSecretValue' via Endpoint" --> SecretsManager_Endpoint
    SecretsManager_Endpoint -- "PrivateLink" --> SecretsManager
    
    SecretsManager -- "2.Returns DB Credentials" --> Fargate_Service
    
    Fargate_Service -- "3.Connects to DB using fetched credentials" --> App_RDS
    
    style AWS_Cloud fill:#FFDAB9,stroke:#333,stroke-width:2px
```

#### 3. Component-to-Resource Mapping Table

| Logical Component | Physical Resource | Rationale for Choice |
| :--- | :--- | :--- |
| **Secrets Vault** | **AWS Secrets Manager** | **Secure, Managed, & Integrated:** AWS Secrets Manager is a dedicated service for securely storing and managing the lifecycle of secrets. Its key advantage is the deep integration with IAM for fine-grained permissions and with services like RDS for automatic credential rotation, which significantly enhances the security posture. |
| *(New Resource)*| **Secrets Manager VPC Endpoint**| **Enhanced Security:** To allow services in our private subnets to access Secrets Manager without their traffic traversing the public internet, a VPC Endpoint is used. This ensures that even the requests for secrets are kept on the private AWS network, providing an essential layer of security. |
| **Application Services**| **AWS Fargate Tasks (with IAM Task Roles)** | **Secure Identity:** The Fargate services are assigned specific IAM Task Roles. This gives each running container a secure identity that can be used to authenticate with other AWS services like Secrets Manager, following the principle of least privilege. |

#### 4. Overall Logical View (C4 Component Diagram)

```mermaid
graph TD
    %% --- External Actors & Systems ---
    subgraph "External"
        direction TB
        Admin[Administrator]
        Approver[Manager/Approver]
        HRIS[HRIS System]
        SIEM[SIEM Platform]
    end

    subgraph SystemBoundary ["AI-Powered Guardian System"]
        %% --- User Facing Components ---
        subgraph UserFacing ["User Facing"]
            WebUI["Web UI (SPA)"]
            APIGateway[API Gateway]
        end

        %% --- Backend Services ---
        subgraph BackendServices ["Backend Microservices"]
            RBAC_Service[RBAC Service]
            WorkflowEngine[Workflow Engine]
            IdentitySync[Identity Sync Service]
            AuditService[Audit Service]
        end

        %% --- AI/ML Components ---
        subgraph AI_ML ["AI/ML"]
            AI_Service[AI Anomaly Detection Service]
            ModelRegistry[Model Registry]
        end
        
        %% --- Data Stores ---
        subgraph DataStores ["Data Stores"]
            AppDB[(Application DB)]
            AuditDB[(Audit DB)]
            WorkflowDB[(Workflow State DB)]
            Cache[(Performance Cache)]
        end

        %% --- Messaging & Security ---
        subgraph Messaging ["Messaging & Security"]
            MQ(Message Queue)
            Notifier(Notification Service)
            SecretsVault[Secrets Vault]
        end
    end

    %% --- Logical Flows ---
    Admin -- "Uses" --> WebUI
    WebUI -- "API Calls" --> APIGateway
    APIGateway -- "Routes to" --> RBAC_Service & WorkflowEngine
    
    RBAC_Service -- "Reads/Writes" --> AppDB
    RBAC_Service -- "Uses" --> Cache
    RBAC_Service -- "Gets Risk Score" --> AI_Service
    RBAC_Service -- "Publishes Event" --> MQ
    
    WorkflowEngine -- "Manages State" --> WorkflowDB
    WorkflowEngine -- "Sends Alert" --> Notifier
    WorkflowEngine -- "Grants/Revokes" --> AppDB
    
    IdentitySync -- "Reads from" --> HRIS
    IdentitySync -- "Writes to" --> AppDB
    
    AuditService -- "Consumes from" --> MQ
    AuditService -- "Writes to" --> AuditDB
    
    Notifier -- "Notifies" --> Approver
    
    AI_Service -- "Loads Model from" --> ModelRegistry
    
    AuditDB -- "Source for" --> SIEM
    
    BackendServices -- "Fetch Credentials" --> SecretsVault
    DataStores -- "Credentials Stored in" --> SecretsVault

    style SystemBoundary fill:#f4f4f4,stroke:#333,stroke-width:2px
```

#### 5. Overall Physical View (AWS Deployment Diagram)

```mermaid
graph TD
    subgraph "External Users & Systems"
        User[Administrator / Approver]
        HRIS_API[("3rd Party HRIS API")]
        SIEM_Endpoint[("Bank SIEM Collector")]
    end

    subgraph AWS_Cloud ["AWS Cloud"]
        %% --- Global & Regional Services ---
        CloudFront[("CloudFront (CDN)")] --> S3[("S3 Bucket: Web UI")]
        EventBridge[("EventBridge Scheduler")] --> MLOps_Pipeline
        Observability[("CloudWatch Observability")]
        
        %% --- Main Application VPC ---
        subgraph VPC ["VPC (Multi-AZ)"]
            subgraph Public_Subnets ["Public Subnets"]
                ALB[("Application Load Balancer")]
                NAT[("NAT Gateway")]
            end
            subgraph Private_Compute ["Private Subnets (Compute)"]
                FargateServices[("Fargate Services (Auto Scaled)<br/>RBAC, Audit, Workflow, Identity Sync")]
            end
            subgraph Private_Data ["Private Subnets (Data)"]
                RDS_HA[("RDS Multi-AZ<br/>App & Audit DBs")]
                ElastiCache_HA[("ElastiCache Multi-AZ<br/>Redis Cache")]
            end
            subgraph Private_Endpoints ["Private Subnets (Endpoints)"]
                SecretsManager_Endpoint[("Secrets Manager Endpoint")]
                SageMaker_Endpoint[("SageMaker Endpoint")]
            end
        end

        %% --- AWS Managed Services (Accessed via PrivateLink/IAM) ---
        subgraph AWS_Managed ["AWS Managed Services"]
            SecretsManager[("Secrets Manager")]
            SageMaker[("SageMaker Inference")]
            DynamoDB[("DynamoDB: Workflow State")]
            SQS[("SQS: Audit Queue")]
            SNS[("SNS: Notifications")]
        end

        %% --- Offline MLOps & Data Pipelines ---
        subgraph MLOps_Pipeline ["MLOps & Data Pipelines"]
            StepFunctions[("Step Functions")] --> Glue[("Glue ETL")] & SageMakerTrain[("SageMaker Training")]
            Glue --> S3_DataLake[("S3 Data Lake")]
            SageMakerTrain --> S3_DataLake
            SageMakerTrain --> SageMakerRegistry[("SageMaker Model Registry")]
            Kinesis[("Kinesis Data Firehose")]
        end
    end

    %% --- Primary Connections ---
    User -- "HTTPS" --> CloudFront & APIGW[("API Gateway")]
    APIGW --> ALB
    ALB --> FargateServices
    
    FargateServices -- "IAM + Endpoint" --> SecretsManager
    FargateServices -- "IAM + Endpoint" --> SageMaker
    FargateServices -- "IAM" --> SQS & SNS & DynamoDB
    FargateServices -- "Credentials via Secrets Mgr" --> RDS_HA & ElastiCache_HA
    FargateServices -- "Metrics & Logs" --> Observability
    
    NAT -- "Egress" --> HRIS_API
    
    %% --- Offline Pipeline Connections ---
    Glue -- "Reads via VPC Connector" --> RDS_HA
    SageMakerRegistry -- "Updates Model" --> SageMaker
    RDS_HA -- "CDC Stream" --> Kinesis
    Kinesis -- "Delivers to" --> SIEM_Endpoint

    style AWS_Cloud fill:#FFDAB9,stroke:#333,stroke-width:2px
```
