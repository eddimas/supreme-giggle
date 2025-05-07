import { useEffect, useState } from "react";
import axios from "axios";
import { CheckCircle, Loader, XCircle } from "lucide-react";

export default function WorkflowStatus({ runId, onReset }) {
  const [run, setRun] = useState(null);
  const [error, setError] = useState(null);

  useEffect(() => {
    let interval;
    const fetchStatus = async () => {
      try {
        const res = await axios.get(`/status/${runId}`);
        setRun(res.data);
      } catch (err) {
        setError(err.response?.data || err.message);
        clearInterval(interval);
      }
    };
    fetchStatus();
    interval = setInterval(fetchStatus, 2000);
    return () => clearInterval(interval);
  }, [runId]);

  if (error) {
    return (
      <div className="max-w-xl mx-auto mt-6 bg-red-50 border border-red-200 rounded-xl p-6">
        <h2 className="text-xl font-semibold text-red-700 mb-2">Error</h2>
        <p className="text-red-600">{error}</p>
        <button onClick={onReset} className="mt-4 text-blue-600 underline">
          Try Again
        </button>
      </div>
    );
  }

  if (!run) {
    return <div className="text-center py-8">Loading workflow…</div>;
  }

  return (
    <div className="max-w-3xl mx-auto mt-6 bg-white shadow-lg rounded-2xl p-6">
      <div className="flex justify-between items-center mb-4">
        <h2 className="text-2xl font-bold">Run “{run.name}”</h2>
        <button
          onClick={onReset}
          className="text-sm text-gray-500 hover:text-gray-700"
        >
          New run
        </button>
      </div>
      <div className="mb-6">
        <span
          className={
            `inline-block px-3 py-1 rounded-full text-sm font-medium ` +
            (run.status === "completed"
              ? "bg-green-100 text-green-800"
              : run.status === "failed"
              ? "bg-red-100 text-red-800"
              : "bg-yellow-100 text-yellow-800")
          }
        >
          {run.status.toUpperCase()}
        </span>
      </div>

      <div className="border-l-4 border-gray-200 p-4 space-y-6">
        {run.steps.map((step, idx) => {
          const isDone = idx < run.current;
          const isRunning = idx === run.current && run.status === "running";
          const isFailed = run.status === "failed" && idx === run.current;

          const Icon = isDone ? CheckCircle : isRunning ? Loader : XCircle;
          const iconColor = isDone
            ? "text-green-500"
            : isRunning
            ? "text-yellow-500 animate-spin"
            : isFailed
            ? "text-red-500"
            : "text-gray-300";

          const { started_at, ended_at } = step;
          const start = started_at
            ? new Date(started_at).toLocaleTimeString()
            : "";
          const end = ended_at ? new Date(ended_at).toLocaleTimeString() : "";
          const duration =
            started_at && ended_at
              ? `${((new Date(ended_at) - new Date(started_at)) / 1000).toFixed(
                  1
                )}s`
              : "";

          // progress percent: done=100, running=50, pending=0, failed=100
          const percent = isDone || isFailed ? 100 : isRunning ? 50 : 0;

          return (
            <div key={idx} className="relative">
              <div className="absolute -left-8 top-1">
                <Icon className={`w-6 h-6 ${iconColor}`} />
              </div>
              <div className="bg-gray-50 p-4 rounded-xl">
                <div className="flex justify-between items-center">
                  <h3 className="text-lg font-semibold">{step.name}</h3>
                  <span
                    className={
                      `px-2 py-1 rounded-full text-xs font-medium ` +
                      (isDone
                        ? "bg-green-100 text-green-800"
                        : isRunning
                        ? "bg-yellow-100 text-yellow-800"
                        : isFailed
                        ? "bg-red-100 text-red-800"
                        : "bg-gray-100 text-gray-600")
                    }
                  >
                    {isDone
                      ? "DONE"
                      : isRunning
                      ? "RUNNING"
                      : isFailed
                      ? "FAILED"
                      : "PENDING"}
                  </span>
                </div>
                {(start || end || duration) && (
                  <p className="mt-2 text-sm text-gray-600">
                    {start && <span>{start}</span>}
                    {end && <span> → {end}</span>}
                    {duration && <span> ({duration})</span>}
                  </p>
                )}
                <div className="mt-3 h-2 bg-gray-200 rounded-full overflow-hidden">
                  <div
                    className="h-full bg-green-500 transition-all"
                    style={{ width: `${percent}%` }}
                  />
                </div>
              </div>
            </div>
          );
        })}
      </div>

      <details className="mt-4">
        <summary className="cursor-pointer font-medium">Logs ▼</summary>
        <pre className="mt-2 bg-black text-white p-4 rounded-xl max-h-64 overflow-auto text-sm">
          {run.log.map(
            (entry, i) =>
              `# Step: ${entry.step}\n${JSON.stringify(
                entry.result,
                null,
                2
              )}\n\n`
          )}
        </pre>
      </details>
    </div>
  );
}
