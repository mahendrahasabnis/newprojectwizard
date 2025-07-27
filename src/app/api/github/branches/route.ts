import { NextRequest, NextResponse } from 'next/server';

export async function GET(request: NextRequest) {
  try {
    const { searchParams } = new URL(request.url);
    const repo = searchParams.get('repo');

    if (!repo) {
      return NextResponse.json({ error: 'Repository parameter is required' }, { status: 400 });
    }

    // Check if GitHub token is available
    const githubToken = process.env.GITHUB_PAT;
    
    if (!githubToken || githubToken === 'your_github_personal_access_token_here') {
      // Return demo data if no token
      return NextResponse.json({
        branches: [
          { name: 'main' },
          { name: 'develop' },
          { name: 'feature/new-template' },
          { name: 'hotfix/bug-fix' }
        ]
      });
    }

    // Fetch branches from GitHub API
    const response = await fetch(`https://api.github.com/repos/${repo}/branches`, {
      headers: {
        'Authorization': `token ${githubToken}`,
        'Accept': 'application/vnd.github.v3+json',
        'User-Agent': 'Project-Wizard'
      }
    });

    if (!response.ok) {
      throw new Error(`GitHub API error: ${response.status} ${response.statusText}`);
    }

    const branchesData = await response.json();
    
    // Transform the data to match our interface
    const branches = branchesData.map((branch: { name: string }) => ({
      name: branch.name
    }));

    return NextResponse.json({ branches });
  } catch (error) {
    console.error('Error fetching branches:', error);
    
    // Return demo data on error
    return NextResponse.json({
      branches: [
        { name: 'main' },
        { name: 'develop' },
        { name: 'feature/new-template' },
        { name: 'hotfix/bug-fix' }
      ]
    });
  }
} 