#!/usr/bin/env python3
"""
GitHub Integration Test Script
Tests the complete agent → GitHub → human approval workflow
"""

import os
from dotenv import load_dotenv

def check_github_setup():
    """Check if GitHub integration is properly configured"""
    load_dotenv()
    
    print("🔍 Checking GitHub Integration Setup...")
    
    use_real = os.getenv("USE_REAL_GITHUB", "false").lower() == "true"
    token = os.getenv("GITHUB_TOKEN", "")
    repo = os.getenv("GITHUB_REPO", "")
    
    print(f"USE_REAL_GITHUB: {use_real}")
    print(f"GITHUB_TOKEN: {'✅ Set' if token and token != 'mock_github_token' else '❌ Not set or mock'}")
    print(f"GITHUB_REPO: {repo if repo else '❌ Not set'}")
    
    if not use_real:
        print("\n⚠️  GitHub integration is disabled (using mock)")
        print("To enable: Set USE_REAL_GITHUB=true in .env")
        return False
        
    if not token or token == "mock_github_token":
        print("\n❌ Real GitHub token required")
        print("To fix: Set GITHUB_TOKEN=your_token in .env")
        return False
        
    if not repo:
        print("\n❌ GitHub repository not specified")
        print("To fix: Set GITHUB_REPO=username/repo in .env")
        return False
    
    print("\n✅ GitHub integration configured!")
    return True

def test_github_connection():
    """Test actual GitHub API connection"""
    try:
        from github import Github
        load_dotenv()
        
        token = os.getenv("GITHUB_TOKEN")
        repo_name = os.getenv("GITHUB_REPO")
        
        print(f"\n🔌 Testing connection to {repo_name}...")
        
        g = Github(token)
        user = g.get_user()
        print(f"✅ Authenticated as: {user.login}")
        
        repo = g.get_repo(repo_name)
        print(f"✅ Repository access: {repo.full_name}")
        print(f"✅ Default branch: {repo.default_branch}")
        
        # Check if we can create branches
        branches = list(repo.get_branches())
        print(f"✅ Can read branches: {len(branches)} branches found")
        
        return True
        
    except ImportError:
        print("❌ PyGithub not installed. Run: pip install PyGithub")
        return False
    except Exception as e:
        print(f"❌ GitHub connection failed: {str(e)}")
        return False

def run_agent_test():
    """Run the agent and create a real PR"""
    print("\n🤖 Running S3 Agent with GitHub Integration...")
    
    from agent.core.s3_agent import S3CreationAgent
    
    agent = S3CreationAgent()
    
    print("Processing ticket_004 (IAM access request)...")
    result = agent.process_ticket('ticket_004')
    
    print(f"\n📊 Workflow Result:")
    print(f"Status: {result['status']}")
    print(f"Steps: {len(result['steps'])} completed")
    
    if result['status'] == 'completed':
        print("\n✅ PR should now be created in your GitHub repo!")
        print("🔍 Check: https://github.com/salmansheikhutk/RAG/pulls")
        print("\n👨‍💻 Next steps:")
        print("1. Go to your GitHub repo")
        print("2. Review the generated pull request")
        print("3. Check the Terraform files")
        print("4. Approve and merge (human action required)")
        
    return result

def main():
    """Main test workflow"""
    print("="*60)
    print("🔧 GitHub Integration Test")
    print("="*60)
    
    # Step 1: Check configuration
    if not check_github_setup():
        print("\n❌ Please configure GitHub integration first")
        return
    
    # Step 2: Test connection
    if not test_github_connection():
        print("\n❌ GitHub connection failed")
        return
    
    # Step 3: Run agent
    print("\n" + "="*60)
    print("🚀 Running Agent Test")
    print("="*60)
    
    result = run_agent_test()
    
    print("\n" + "="*60)
    print("📋 Summary")
    print("="*60)
    print("The agent creates PRs, but humans must approve them.")
    print("This is the correct workflow for infrastructure changes!")

if __name__ == "__main__":
    main()
