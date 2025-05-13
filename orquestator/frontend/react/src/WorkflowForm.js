import { useState } from "react";
import axios from "axios";

export default function WorkflowForm({ onStart }) {
  const [name, setName] = useState("deploy");
  const [error, setError] = useState(null);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError(null);
    try {
      const res = await axios.post(`http://localhost:8000/start?name=${name}`);
      onStart(res.data.run_id);
    } catch (err) {
      setError(err.response?.data || err.message);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-2">
      <label className="block">
        Workflow name:
        <input
          value={name}
          onChange={(e) => setName(e.target.value)}
          className="border p-1 ml-2"
        />
      </label>
      <button
        type="submit"
        className="bg-blue-600 text-white px-4 py-2 rounded"
      >
        Start
      </button>
      {error && <p className="text-red-500 mt-2">{error}</p>}
    </form>
  );
}
