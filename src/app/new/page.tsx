'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';

interface CreateProjectForm {
  projectName: string;
  orgDomain: string;
  templateRepo: string;
  templateBranch: string;
  firebaseAccount: string;
}

interface ProgressStep {
  id: string;
  title: string;
  status: 'pending' | 'running' | 'completed' | 'error' | 'in-progress';
  message?: string;
}

interface Repository {
  name: string;
  full_name: string;
  default_branch: string;
}

interface Branch {
  name: string;
}

export default function NewProjectPage() {
  const router = useRouter();
  const [formData, setFormData] = useState<CreateProjectForm>({
    projectName: '',
    orgDomain: '',
    templateRepo: '',
    templateBranch: '',
    firebaseAccount: ''
  });
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');
  const [repositories, setRepositories] = useState<Repository[]>([]);
  const [branches, setBranches] = useState<Branch[]>([]);
  const [loadingRepos, setLoadingRepos] = useState(false);
  const [loadingBranches, setLoadingBranches] = useState(false);
  const [progressSteps, setProgressSteps] = useState<ProgressStep[]>([
    { id: 'clone', title: 'Cloning template repository', status: 'pending' },
    { id: 'rename', title: 'Renaming project identifiers', status: 'pending' },
    { id: 'firebase', title: 'Creating Firebase project', status: 'pending' },
    { id: 'apps', title: 'Creating Firebase apps', status: 'pending' },
    { id: 'firestore', title: 'Setting up Firestore database', status: 'pending' },
    { id: 'config', title: 'Downloading Firebase config files', status: 'pending' },
    { id: 'commit', title: 'Committing and pushing changes', status: 'pending' },
    { id: 'privateRepo', title: 'Creating new private repository', status: 'pending' },
    { id: 'baseBuildTag', title: 'Creating base build tag', status: 'pending' },
    { id: 'finalize', title: 'Finalizing project setup', status: 'pending' }
  ]);

  // Fetch repositories on component mount
  useEffect(() => {
    fetchRepositories();
  }, []);

  // Fetch branches when repository changes
  useEffect(() => {
    if (formData.templateRepo) {
      fetchBranches(formData.templateRepo);
    } else {
      setBranches([]);
    }
  }, [formData.templateRepo]);

  const fetchRepositories = async () => {
    setLoadingRepos(true);
    try {
      const response = await fetch('/api/github/repositories');
      if (response.ok) {
        const data = await response.json();
        setRepositories(data.repositories);
        // Set default repository if available
        if (data.repositories.length > 0) {
          setFormData(prev => ({
            ...prev,
            templateRepo: data.repositories[0].full_name
          }));
        }
      } else {
        console.error('Failed to fetch repositories');
      }
    } catch (error) {
      console.error('Error fetching repositories:', error);
    } finally {
      setLoadingRepos(false);
    }
  };

  const fetchBranches = async (repoFullName: string) => {
    setLoadingBranches(true);
    try {
      const response = await fetch(`/api/github/branches?repo=${encodeURIComponent(repoFullName)}`);
      if (response.ok) {
        const data = await response.json();
        setBranches(data.branches);
        // Set default branch if available
        if (data.branches.length > 0) {
          setFormData(prev => ({
            ...prev,
            templateBranch: data.branches[0].name
          }));
        }
      } else {
        console.error('Failed to fetch branches');
        setBranches([]);
      }
    } catch (error) {
      console.error('Error fetching branches:', error);
      setBranches([]);
    } finally {
      setLoadingBranches(false);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    setError('');
    
    // Reset progress steps
    setProgressSteps(steps => steps.map(step => ({ ...step, status: 'pending' as const })));

    try {
      // Start real-time progress updates
      const eventSource = new EventSource('/api/createProject?stream=true');
      
      eventSource.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          setProgressSteps(prev => prev.map((step, index) => {
            if (index < data.step) {
              return { ...step, status: 'completed' as const };
            } else if (index === data.step) {
              return { ...step, status: data.status as 'pending' | 'running' | 'completed' | 'error' | 'in-progress', message: data.message };
            } else {
              return { ...step, status: 'pending' as const };
            }
          }));
        } catch (error) {
          console.error('Error parsing progress update:', error);
        }
      };

      eventSource.onerror = () => {
        eventSource.close();
      };

      // Make the actual project creation request
      const response = await fetch('/api/createProject', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(formData),
      });

      // Close the event source
      eventSource.close();

      const data = await response.json();

      if (data.success) {
        // Mark all steps as completed
        setProgressSteps(prev => prev.map(step => ({ ...step, status: 'completed' as const })));
        
        // Redirect to success page with all the data
        const params = new URLSearchParams({
          projectName: formData.projectName,
          firebaseProjectId: data.firebaseProjectId,
          githubUrl: data.githubUrl,
          newRepoUrl: data.newRepoUrl,
          baseBuildTag: data.baseBuildTag,
          branch: formData.templateBranch,
          firebaseUrl: data.firebaseUrl
        });
        router.push(`/success?${params.toString()}`);
      } else {
        // Mark current step as error
        setProgressSteps(prev => prev.map((step, index) => {
          if (index === data.currentStep || index === prev.length - 1) {
            return { ...step, status: 'error' as const };
          }
          return step;
        }));
        setError(data.error || 'Project creation failed');
      }
    } catch (error) {
      console.error('Network error occurred:', error);
      setError('Network error occurred');
    } finally {
      setIsLoading(false);
    }
  };

  const handleInputChange = (field: keyof CreateProjectForm, value: string) => {
    setFormData(prev => ({ ...prev, [field]: value }));
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-2xl mx-auto">
        <div className="bg-white rounded-lg shadow-xl p-8">
          <div className="text-center mb-8">
            <h1 className="text-3xl font-bold text-gray-900 mb-2">
              🚀 Project Wizard
            </h1>
            <p className="text-gray-600">
              Automate your project setup with Firebase and GitHub integration
            </p>
          </div>

          <form onSubmit={handleSubmit} className="space-y-6">
            {/* Project Name */}
            <div>
              <label htmlFor="projectName" className="block text-sm font-medium text-gray-700 mb-2">
                Project Name *
              </label>
              <input
                type="text"
                id="projectName"
                value={formData.projectName}
                onChange={(e) => handleInputChange('projectName', e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                placeholder="my-awesome-project"
                required
              />
              <p className="mt-1 text-sm text-gray-500">
                Use lowercase letters, numbers, and hyphens only
              </p>
            </div>

            {/* Organization Domain */}
            <div>
              <label htmlFor="orgDomain" className="block text-sm font-medium text-gray-700 mb-2">
                Organization Domain *
              </label>
              <input
                type="text"
                id="orgDomain"
                value={formData.orgDomain}
                onChange={(e) => handleInputChange('orgDomain', e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                placeholder="mycompany"
                required
              />
              <p className="mt-1 text-sm text-gray-500">
                Used for bundle IDs (e.g., com.mycompany.projectname)
              </p>
            </div>

            {/* Firebase Account */}
            <div>
              <label htmlFor="firebaseAccount" className="block text-sm font-medium text-gray-700 mb-2">
                Firebase Account *
              </label>
              <input
                type="email"
                id="firebaseAccount"
                value={formData.firebaseAccount}
                onChange={(e) => handleInputChange('firebaseAccount', e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                placeholder="user@example.com"
                required
              />
              <p className="mt-1 text-sm text-gray-500">
                Firebase account where the project will be created
              </p>
            </div>

            {/* Template Repository Dropdown */}
            <div>
              <label htmlFor="templateRepo" className="block text-sm font-medium text-gray-700 mb-2">
                Template Repository *
              </label>
              <select
                id="templateRepo"
                value={formData.templateRepo}
                onChange={(e) => handleInputChange('templateRepo', e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                required
                disabled={loadingRepos}
              >
                <option value="">Select a repository...</option>
                {repositories.map((repo) => (
                  <option key={repo.full_name} value={repo.full_name}>
                    {repo.full_name}
                  </option>
                ))}
              </select>
              {loadingRepos && (
                <p className="mt-1 text-sm text-gray-500">Loading repositories...</p>
              )}
            </div>

            {/* Template Branch Dropdown */}
            <div>
              <label htmlFor="templateBranch" className="block text-sm font-medium text-gray-700 mb-2">
                Template Branch *
              </label>
              <select
                id="templateBranch"
                value={formData.templateBranch}
                onChange={(e) => handleInputChange('templateBranch', e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                required
                disabled={loadingBranches || !formData.templateRepo}
              >
                <option value="">Select a branch...</option>
                {branches.map((branch) => (
                  <option key={branch.name} value={branch.name}>
                    {branch.name}
                  </option>
                ))}
              </select>
              {loadingBranches && (
                <p className="mt-1 text-sm text-gray-500">Loading branches...</p>
              )}
              {!formData.templateRepo && (
                <p className="mt-1 text-sm text-gray-500">Please select a repository first</p>
              )}
            </div>

            {/* Progress Steps */}
            {isLoading && (
              <div className="mt-8">
                <h3 className="text-lg font-medium text-gray-900 mb-4">Setting up your project...</h3>
                <div className="space-y-3">
                  {progressSteps.map((step) => (
                    <div key={step.id} className="flex items-center space-x-3">
                      <div className={`w-6 h-6 rounded-full flex items-center justify-center text-sm font-medium ${
                        step.status === 'completed' ? 'bg-green-500 text-white' :
                        step.status === 'running' ? 'bg-blue-500 text-white' :
                        step.status === 'error' ? 'bg-red-500 text-white' :
                        'bg-gray-200 text-gray-600'
                      }`}>
                        {step.status === 'completed' ? '✓' :
                         step.status === 'running' ? '⟳' :
                         step.status === 'error' ? '✗' : '○'}
                      </div>
                      <span className={`text-sm ${
                        step.status === 'completed' ? 'text-green-600' :
                        step.status === 'running' ? 'text-blue-600' :
                        step.status === 'error' ? 'text-red-600' :
                        'text-gray-500'
                      }`}>
                        {step.title}
                      </span>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Error Message */}
            {error && (
              <div className="bg-red-50 border border-red-200 rounded-md p-4">
                <div className="flex">
                  <div className="flex-shrink-0">
                    <svg className="h-5 w-5 text-red-400" viewBox="0 0 20 20" fill="currentColor">
                      <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
                    </svg>
                  </div>
                  <div className="ml-3">
                    <h3 className="text-sm font-medium text-red-800">Error</h3>
                    <div className="mt-2 text-sm text-red-700">{error}</div>
                  </div>
                </div>
              </div>
            )}

            {/* Submit Button */}
            <button
              type="submit"
              disabled={isLoading || !formData.templateRepo || !formData.templateBranch}
              className="w-full bg-blue-600 text-white py-3 px-4 rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            >
              {isLoading ? 'Creating Project...' : 'Create Project'}
            </button>
          </form>
        </div>
      </div>
    </div>
  );
} 