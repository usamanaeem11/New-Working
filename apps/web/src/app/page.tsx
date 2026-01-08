export default function Home() {
  return (
    <main className="min-h-screen bg-gradient-to-br from-blue-50 to-purple-50">
      <div className="container mx-auto px-4 py-16">
        <div className="text-center">
          <h1 className="text-6xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-blue-600 to-purple-600 mb-6">
            Working Tracker
          </h1>
          <p className="text-2xl text-gray-700 mb-8">
            Enterprise Workforce Intelligence Platform
          </p>
          <div className="flex gap-4 justify-center">
            <a href="/dashboard" className="px-8 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition">
              Get Started
            </a>
            <a href="/api/docs" className="px-8 py-3 bg-white text-blue-600 border-2 border-blue-600 rounded-lg hover:bg-blue-50 transition">
              View Docs
            </a>
          </div>
        </div>
      </div>
    </main>
  )
}
