import { useState } from "react";
import { AlertCircle, CheckCircle, XCircle, Loader2 } from "lucide-react";
import { analyzeText } from "./services/api";

function App() {
  // ============================================================================
  // STATE MANAGEMENT
  // ============================================================================
  // Why: React needs state to track UI changes and re-render
  // What: Track input text, results, loading state, errors
  // Without: Static UI that doesn't respond to user actions

  const [text, setText] = useState("");
  const [results, setResults] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);

  // ============================================================================
  // HANDLE ANALYZE
  // ============================================================================
  // Why: Core functionality - send text to backend
  // What: Calls API, handles loading states, displays results
  // Without: No way to analyze text

  const handleAnalyze = async () => {
    // Validation
    if (!text.trim()) {
      setError("Please enter some text to analyze");
      return;
    }

    if (text.length < 10) {
      setError("Text must be at least 10 characters long");
      return;
    }

    // Reset states
    setError(null);
    setResults(null);
    setIsLoading(true);

    try {
      const response = await analyzeText(text);
      setResults(response);
    } catch (err) {
      setError(err.message || "Failed to analyze text. Please try again.");
    } finally {
      setIsLoading(false);
    }
  };

  // ============================================================================
  // HANDLE CLEAR
  // ============================================================================

  const handleClear = () => {
    setText("");
    setResults(null);
    setError(null);
  };

  // ============================================================================
  // GET VERDICT COLOR AND ICON
  // ============================================================================

  const getVerdictStyle = (verdict) => {
    if (verdict === "FAKE") {
      return {
        icon: <XCircle className="w-12 h-12" />,
        bgColor: "bg-red-50",
        borderColor: "border-red-200",
        textColor: "text-red-700",
        accentColor: "text-red-600",
      };
    } else if (verdict === "REAL") {
      return {
        icon: <CheckCircle className="w-12 h-12" />,
        bgColor: "bg-green-50",
        borderColor: "border-green-200",
        textColor: "text-green-700",
        accentColor: "text-green-600",
      };
    } else {
      return {
        icon: <AlertCircle className="w-12 h-12" />,
        bgColor: "bg-yellow-50",
        borderColor: "border-yellow-200",
        textColor: "text-yellow-700",
        accentColor: "text-yellow-600",
      };
    }
  };

  // ============================================================================
  // RENDER
  // ============================================================================

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-purple-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b border-gray-200">
        <div className="max-w-5xl mx-auto px-4 py-6">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-gradient-to-br from-blue-500 to-purple-600 rounded-lg flex items-center justify-center">
              <span className="text-white font-bold text-xl">🔍</span>
            </div>
            <div>
              <h1 className="text-2xl font-bold text-gray-900">
                Fake News Detector
              </h1>
              <p className="text-sm text-gray-600">
                AI-powered truth verification
              </p>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-5xl mx-auto px-4 py-8">
        {/* Input Section */}
        <div className="bg-white rounded-xl shadow-lg border border-gray-200 p-6 mb-6">
          <label className="block text-sm font-semibold text-gray-700 mb-3">
            Enter news article or claim to analyze
          </label>
          <textarea
            value={text}
            onChange={(e) => setText(e.target.value)}
            placeholder="Paste your news article, headline, or claim here..."
            className="w-full h-48 px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none text-gray-900 placeholder-gray-400"
            disabled={isLoading}
          />

          {/* Character Count */}
          <div className="flex items-center justify-between mt-3">
            <span className="text-sm text-gray-500">
              {text.length} characters
            </span>
            <div className="flex gap-3">
              {text && (
                <button
                  onClick={handleClear}
                  className="px-4 py-2 text-gray-700 bg-gray-100 hover:bg-gray-200 rounded-lg font-medium transition-colors"
                  disabled={isLoading}
                >
                  Clear
                </button>
              )}
              <button
                onClick={handleAnalyze}
                disabled={isLoading || !text.trim()}
                className="px-6 py-2 bg-gradient-to-r from-blue-500 to-purple-600 text-white rounded-lg font-medium hover:from-blue-600 hover:to-purple-700 disabled:opacity-50 disabled:cursor-not-allowed transition-all flex items-center gap-2"
              >
                {isLoading ? (
                  <>
                    <Loader2 className="w-4 h-4 animate-spin" />
                    Analyzing...
                  </>
                ) : (
                  "Analyze"
                )}
              </button>
            </div>
          </div>
        </div>

        {/* Error Message */}
        {error && (
          <div className="bg-red-50 border border-red-200 rounded-lg p-4 mb-6 flex items-start gap-3">
            <AlertCircle className="w-5 h-5 text-red-600 flex-shrink-0 mt-0.5" />
            <div>
              <h3 className="font-semibold text-red-900">Error</h3>
              <p className="text-red-700 text-sm mt-1">{error}</p>
            </div>
          </div>
        )}

        {/* Results Section */}
        {results && (
          <div className="space-y-6">
            {/* Main Verdict Card */}
            <div
              className={`${getVerdictStyle(results.verdict).bgColor} ${
                getVerdictStyle(results.verdict).borderColor
              } border-2 rounded-xl p-8`}
            >
              <div className="flex items-start gap-6">
                <div className={getVerdictStyle(results.verdict).accentColor}>
                  {getVerdictStyle(results.verdict).icon}
                </div>
                <div className="flex-1">
                  <h2
                    className={`text-3xl font-bold ${
                      getVerdictStyle(results.verdict).textColor
                    } mb-2`}
                  >
                    {results.verdict}
                  </h2>
                  <div className="flex items-center gap-4 mb-4">
                    <div>
                      <span className="text-sm text-gray-600">Confidence:</span>
                      <span
                        className={`ml-2 text-xl font-bold ${
                          getVerdictStyle(results.verdict).textColor
                        }`}
                      >
                        {(results.confidence * 100).toFixed(1)}%
                      </span>
                    </div>
                    <div className="text-gray-400">•</div>
                    <div>
                      <span className="text-sm text-gray-600">
                        Processed in {results.processing_time_ms.toFixed(0)}ms
                      </span>
                    </div>
                  </div>
                  <p className="text-gray-700 leading-relaxed">
                    {results.reasoning}
                  </p>
                </div>
              </div>

              {/* Confidence Bar */}
              <div className="mt-6">
                <div className="w-full bg-gray-200 rounded-full h-2">
                  <div
                    className={`h-2 rounded-full ${
                      results.verdict === "FAKE"
                        ? "bg-red-600"
                        : results.verdict === "REAL"
                        ? "bg-green-600"
                        : "bg-yellow-600"
                    }`}
                    style={{ width: `${results.confidence * 100}%` }}
                  />
                </div>
              </div>
            </div>

            {/* AI Model Details */}
            <div className="bg-white rounded-xl shadow-lg border border-gray-200 p-6">
              <h3 className="text-lg font-bold text-gray-900 mb-4">
                🤖 AI Model Analysis
              </h3>
              <div className="grid grid-cols-2 gap-4">
                <div className="bg-gray-50 rounded-lg p-4">
                  <p className="text-sm text-gray-600 mb-1">Prediction</p>
                  <p className="text-xl font-bold text-gray-900">
                    {results.ml_prediction}
                  </p>
                </div>
                <div className="bg-gray-50 rounded-lg p-4">
                  <p className="text-sm text-gray-600 mb-1">Confidence</p>
                  <p className="text-xl font-bold text-gray-900">
                    {(results.ml_confidence * 100).toFixed(1)}%
                  </p>
                </div>
              </div>
            </div>

            {/* Fact Checks */}
            {results.fact_checks && results.fact_checks.length > 0 && (
              <div className="bg-white rounded-xl shadow-lg border border-gray-200 p-6">
                <h3 className="text-lg font-bold text-gray-900 mb-4">
                  ✓ Professional Fact Checks
                </h3>
                <div className="space-y-3">
                  {results.fact_checks.map((fc, idx) => (
                    <div
                      key={idx}
                      className="bg-blue-50 border border-blue-200 rounded-lg p-4"
                    >
                      <p className="font-semibold text-gray-900 mb-2">
                        "{fc.claim}"
                      </p>
                      <div className="flex items-center gap-4 text-sm">
                        <span className="text-gray-600">
                          Rating:{" "}
                          <span className="font-semibold">{fc.rating}</span>
                        </span>
                        <span className="text-gray-400">•</span>
                        <span className="text-gray-600">
                          Source: {fc.source}
                        </span>
                        {fc.url && (
                          <>
                            <span className="text-gray-400">•</span>
                            <a
                              href={fc.url}
                              target="_blank"
                              rel="noopener noreferrer"
                              className="text-blue-600 hover:underline"
                            >
                              View Details
                            </a>
                          </>
                        )}
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        )}

        {/* Sample Texts */}
        {!results && !isLoading && (
          <div className="bg-white rounded-xl shadow-lg border border-gray-200 p-6">
            <h3 className="text-lg font-bold text-gray-900 mb-4">
              💡 Try These Examples
            </h3>
            <div className="space-y-2">
              {[
                "Scientists have discovered that drinking water daily is beneficial for health and helps maintain proper bodily functions.",
                "Breaking: The government has secretly replaced all birds with surveillance drones. Wake up people!",
                "New study from Harvard Medical School shows that regular exercise can reduce the risk of heart disease by up to 30%.",
              ].map((example, idx) => (
                <button
                  key={idx}
                  onClick={() => setText(example)}
                  className="w-full text-left p-3 bg-gray-50 hover:bg-gray-100 rounded-lg text-sm text-gray-700 transition-colors"
                >
                  {example}
                </button>
              ))}
            </div>
          </div>
        )}
      </main>

      {/* Footer */}
      <footer className="max-w-5xl mx-auto px-4 py-8 text-center text-gray-600 text-sm">
        <p>
          Powered by AI and professional fact-checkers • Built with React,
          FastAPI, and Transformers
        </p>
      </footer>
    </div>
  );
}

export default App;
