import { NextResponse } from 'next/server';

export async function GET() {
  try {
    // Check if GitHub token is available
    const githubToken = process.env.GITHUB_PAT;
    
    if (!githubToken || githubToken === 'your_github_personal_access_token_here') {
      // Return demo data if no token
      return NextResponse.json({
        repositories: [
          { name: 'mytemplate-app', full_name: 'mahendrahasabnis/mytemplate-app', default_branch: 'main' }
        ]
      });
    }

    // Fetch repositories from GitHub API
    const response = await fetch('https://api.github.com/user/repos', {
      headers: {
        'Authorization': `token ${githubToken}`,
        'Accept': 'application/vnd.github.v3+json',
        'User-Agent': 'Project-Wizard'
      }
    });

    if (!response.ok) {
      throw new Error(`GitHub API error: ${response.status} ${response.statusText}`);
    }

    const repos = await response.json();
    
    // Transform the data to match our interface
    const repositories = repos.map((repo: {
      name: string;
      full_name: string;
      default_branch: string;
    }) => ({
      name: repo.name,
      full_name: repo.full_name,
      default_branch: repo.default_branch
    }));

    return NextResponse.json({ repositories });
  } catch (error) {
    console.error('Error fetching repositories:', error);
    
    // Return demo data on error
    return NextResponse.json({
      repositories: [
        { name: 'mytemplate-app', full_name: 'mahendrahasabnis/mytemplate-app', default_branch: 'main' }
      ]
    });
  }
} 