from core.github_client import github_api
from engines.xai_explainer import xai_engine
from engines.nlp_codebert import nlp_engine
from engines.ast_analyzer import ast_engine
from engines.rag_python_imports import rag_engine
from services.pr_gatekeeper import gatekeeper
from core.logger import logger

def process_pipeline(repo_name: str, pr_number: int, head_sha: str):
    logger.info(f"Starting Deep Python Pipeline for {repo_name} PR #{pr_number}")
    
    pr_files = github_api.get_pr_files(repo_name, pr_number)
    if not pr_files: return

    # 1. Extract Metrics for ML
    la = sum(f.get("additions", 0) for f in pr_files)
    ld = sum(f.get("deletions", 0) for f in pr_files)
    nf = len(pr_files)

    # 2. XAI Deployment Risk Analysis
    risk_score, xai_report = xai_engine.analyze_risk(la, ld, nf)

    # 3. Python File Deep Scans
    nlp_report = "### 🛡️ CodeBERT Semantic Security\n\n"
    ast_report = "### 🔬 AST Structural Analysis\n\n"
    rag_report = "### 🔗 Integration Dependencies Detected\n"
    
    has_py_files = False

    for file_data in pr_files:
        filename = file_data.get("filename", "")
        if not filename.endswith(".py"): continue
        
        has_py_files = True
        raw_code = github_api.fetch_raw_code(file_data.get("raw_url", ""))
        if not raw_code: continue

        # CodeBERT
        nlp_report += nlp_engine.scan(raw_code, filename) + "\n"
        
        # AST
        ast_res = ast_engine.scan(raw_code, filename)
        if ast_res: ast_report += f"#### 📄 `{filename}`\n{ast_res}\n"

        # RAG Context
        deps = rag_engine.extract_dependencies(raw_code)
        if deps: rag_report += f"* `{filename}` imports: {', '.join(deps)}\n"

    # 4. Aggregation & Posting
    final_report = "## 🚀 Enterprise Python XAI Review\n\n"
    final_report += f"{xai_report}\n---\n"
    
    if has_py_files:
        final_report += f"{nlp_report}\n---\n{ast_report}\n---\n{rag_report}"
    else:
        final_report += "No `.py` files modified. Deep scans skipped."

    github_api.post_comment(repo_name, pr_number, final_report)

    # 5. The Hard Gate (Blast Radius Enforcement)
    gatekeeper.evaluate_and_enforce(repo_name, head_sha, risk_score)