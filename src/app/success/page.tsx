'use client';

import { useSearchParams } from 'next/navigation';
import Link from 'next/link';
import { Suspense } from 'react';

function SuccessContent() {
  const searchParams = useSearchParams();
  const projectName = searchParams.get('projectName');
  const firebaseProjectId = searchParams.get('firebaseProjectId');
  const newRepoUrl = searchParams.get('newRepoUrl');
  const baseBuildTag = searchParams.get('baseBuildTag');
  const branch = searchParams.get('branch');
  const isDemo = searchParams.get('demo') === 'true';

  return (
    <div className="min-h-screen bg-gradient-to-br from-green-50 to-emerald-100 py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-2xl mx-auto">
        <div className="bg-white rounded-lg shadow-xl p-8">
          <div className="text-center mb-8">
            <div className="mx-auto flex items-center justify-center h-12 w-12 rounded-full bg-green-100 mb-4">
              <svg className="h-6 w-6 text-green-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
              </svg>
            </div>
            <h1 className="text-3xl font-bold text-gray-900 mb-2">
              🎉 Project Created Successfully!
            </h1>
            <p className="text-gray-600">
              Your project &quot;{projectName}&quot; has been set up with Firebase and GitHub integration.
            </p>
            
            {isDemo && (
              <div className="mt-4 p-3 bg-yellow-100 border border-yellow-300 rounded-lg">
                <p className="text-sm text-yellow-800 font-medium">
                  🎭 Demo Mode - This was a simulation. Set up real tokens to create actual projects.
                </p>
              </div>
            )}
          </div>

          <div className="space-y-4">
            <div className="bg-green-50 border border-green-200 rounded-lg p-4">
              <h3 className="text-lg font-semibold text-green-800 mb-2">✅ Project Created Successfully!</h3>
              <p className="text-green-700">Your new project &quot;{projectName}&quot; has been set up with all Firebase services.</p>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                <h4 className="font-semibold text-blue-800 mb-2">Firebase Project</h4>
                <p className="text-blue-700 text-sm mb-2">Project ID: {firebaseProjectId}</p>
                <a 
                  href={`https://console.firebase.google.com/project/${firebaseProjectId}`}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-blue-600 hover:text-blue-800 text-sm underline"
                >
                  Open Firebase Console →
                </a>
              </div>

              <div className="bg-purple-50 border border-purple-200 rounded-lg p-4">
                <h4 className="font-semibold text-purple-800 mb-2">GitHub Repository</h4>
                <p className="text-purple-700 text-sm mb-2">Branch: {branch}</p>
                <a 
                  href={searchParams.get('githubUrl') || '#'}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-purple-600 hover:text-purple-800 text-sm underline"
                >
                  View Repository →
                </a>
              </div>

              <div className="bg-orange-50 border border-orange-200 rounded-lg p-4">
                <h4 className="font-semibold text-orange-800 mb-2">New Private Repository</h4>
                <p className="text-orange-700 text-sm mb-2">Base build stored in private repo</p>
                <a 
                  href={newRepoUrl || '#'}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-orange-600 hover:text-orange-800 text-sm underline"
                >
                  View Private Repository →
                </a>
              </div>

              <div className="bg-indigo-50 border border-indigo-200 rounded-lg p-4">
                <h4 className="font-semibold text-indigo-800 mb-2">Base Build Tag</h4>
                <p className="text-indigo-700 text-sm mb-2">Tag: {baseBuildTag || 'base-build-' + new Date().toISOString().split('T')[0]}</p>
                <p className="text-indigo-600 text-xs">Tagged for version control</p>
              </div>
            </div>

            <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-6">
              <h3 className="text-lg font-medium text-yellow-900 mb-2">Next Steps</h3>
              <ul className="text-yellow-800 space-y-2">
                <li>• Clone the new branch from GitHub</li>
                <li>• Review the Firebase configuration files (firebase.json, firestore.rules, storage.rules)</li>
                <li>• Check the Flutter Firebase config in lib/firebase_config.dart</li>
                <li>• Update security rules after testing period (1 year from creation)</li>
                <li>• Set up your development environment</li>
                <li>• Start building your application!</li>
              </ul>
            </div>

            <div className="text-center">
              <Link
                href="/new"
                className="inline-block mt-6 px-6 py-3 bg-green-600 text-white rounded-md shadow hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-green-500 focus:ring-offset-2 transition-colors"
              >
                Create Another Project
              </Link>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default function SuccessPage() {
  return (
    <Suspense>
      <SuccessContent />
    </Suspense>
  );
} 