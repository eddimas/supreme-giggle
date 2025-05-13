import { useState } from "react";
import WorkflowForm from "./WorkflowForm";
import WorkflowStatus from "./WorkflowStatus";

function App() {
  const [runId, setRunId] = useState(null);

  return (
    <div className="p-4 max-w-xl mx-auto">
      <h1 className="text-2xl font-bold mb-4">Orquestator UI</h1>
      {!runId ? (
        <WorkflowForm onStart={setRunId} />
      ) : (
        <WorkflowStatus runId={runId} onReset={() => setRunId(null)} />
      )}
    </div>
  );
}

export default App;
