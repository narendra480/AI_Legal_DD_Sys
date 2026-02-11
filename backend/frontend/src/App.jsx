import { useState } from "react";

export default function App() {
  const [files, setFiles] = useState([]);
  const [question, setQuestion] = useState("");
  const [answer, setAnswer] = useState("");

  const [uploadStatus, setUploadStatus] = useState("");
  const [isUploading, setIsUploading] = useState(false);
  const [isAsking, setIsAsking] = useState(false);

  const [ddSummary, setDdSummary] = useState({
    status: "",
    documents: {},
    heat_map: [],
  });

  const [isLoadingDD, setIsLoadingDD] = useState(false);

  // ===============================
  // Upload PDFs
  // ===============================
  const uploadFiles = async () => {
    if (!files.length) {
      setUploadStatus("Please select at least one PDF");
      return;
    }

    setIsUploading(true);
    setUploadStatus("Processing documents…");

    try {
      for (let i = 0; i < files.length; i++) {
        const formData = new FormData();
        formData.append("file", files[i]);

        const resetFlag = i === 0 ? "&reset=true" : "";

        await fetch(
          `http://127.0.0.1:8000/extract_pdf_text/?use_ocr=false${resetFlag}`,
          { method: "POST", body: formData }
        );
      }
      setUploadStatus("Uploaded & indexed successfully");
    } catch {
      setUploadStatus("Upload failed. Please try again.");
    } finally {
      setIsUploading(false);
    }
  };

  // ===============================
  // Ask Question
  // ===============================
  const askQuestion = async () => {
    if (!question.trim()) return;

    setIsAsking(true);
    setAnswer("");

    try {
      const res = await fetch("http://127.0.0.1:8000/ask", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ question }),
      });
      const data = await res.json();
      setAnswer(data.answer || "");
    } catch {
      setAnswer("Unable to generate answer.");
    } finally {
      setIsAsking(false);
    }
  };

  // ===============================
  // Load DD Summary
  // ===============================
  const loadDDSummary = async () => {
    setIsLoadingDD(true);
    try {
      const res = await fetch("http://127.0.0.1:8000/due-diligence/summary");
      const data = await res.json();
      setDdSummary(data);
    } catch {
      alert("Failed to load DD summary");
    } finally {
      setIsLoadingDD(false);
    }
  };

  const downloadDDReport = () => {
    window.location.href = "http://127.0.0.1:8000/due-diligence/report";
  };

  // ===============================
  // Helpers
  // ===============================
  const severityColor = (level) => {
    if (level === "High") return "bg-red-50 border-red-400";
    if (level === "Medium") return "bg-yellow-50 border-yellow-400";
    return "bg-green-50 border-green-400";
  };

  const flags = ddSummary.heat_map.filter((r) => r.severity === "High");

  return (
    <div className="min-h-screen bg-slate-50 px-6 py-10 space-y-10">

      {/* ================= CORPORATE GRADIENT CARD ================= */}
      <div className="max-w-4xl mx-auto rounded-2xl shadow-xl border-l-8 border-indigo-600
        bg-gradient-to-br from-indigo-50 via-slate-50 to-white p-8 space-y-6">

        <h1 className="text-2xl font-bold text-indigo-700">
          AI Legal Due Diligence Assistant
        </h1>

        <div className="flex items-center gap-4">
          <input
            type="file"
            multiple
            accept="application/pdf"
            onChange={(e) => setFiles(e.target.files)}
            className="text-sm"
          />
          <button
            onClick={uploadFiles}
            disabled={isUploading}
            className="bg-indigo-600 hover:bg-indigo-700 text-white px-5 py-2 rounded-md shadow"
          >
            {isUploading ? "Uploading…" : "Upload & Index"}
          </button>
        </div>

        {uploadStatus && (
          <p className="text-sm text-slate-600">{uploadStatus}</p>
        )}

        <input
          value={question}
          onChange={(e) => setQuestion(e.target.value)}
          placeholder="Ask a legal or risk-related question"
          className="w-full border rounded-md px-4 py-2"
        />

        <button
          onClick={askQuestion}
          disabled={isAsking}
          className="bg-emerald-600 hover:bg-emerald-700 text-white px-4 py-2 rounded-md"
        >
          {isAsking ? "Thinking…" : "Ask"}
        </button>

        {answer && (
          <div className="bg-emerald-50 border border-emerald-200 rounded-md p-4 text-sm">
            {answer}
          </div>
        )}
      </div>

      {/* ================= ACTION BUTTONS ================= */}
      <div className="flex justify-center gap-4">
        <button
          onClick={loadDDSummary}
          disabled={isLoadingDD}
          className="bg-slate-800 text-white px-6 py-2 rounded-md shadow"
        >
          {isLoadingDD ? "Generating…" : "Generate Due Diligence Summary"}
        </button>

        {ddSummary.status === "success" && (
          <button
            onClick={downloadDDReport}
            className="bg-indigo-600 text-white px-6 py-2 rounded-md shadow"
          >
            📄 Download DD Report
          </button>
        )}
      </div>

      {/* ================= DD SUMMARY ================= */}
      <div className="max-w-5xl mx-auto space-y-6">
        {Object.entries(ddSummary.documents).map(([docName, doc], i) => (
          <div
            key={i}
            className={`border rounded-xl p-5 ${severityColor(
              doc.overall_risk
            )}`}
          >
            <h3 className="text-lg font-semibold mb-1">📄 {docName}</h3>
            <p className="text-sm mb-3">
              Type: {doc.doc_type} | Overall Risk:{" "}
              <strong>{doc.overall_risk}</strong>
            </p>

            <div className="grid grid-cols-4 gap-3 text-center text-sm mb-3">
              <div className="bg-red-100 p-2 rounded">High<br />{doc.risk_counts.High}</div>
              <div className="bg-yellow-100 p-2 rounded">Medium<br />{doc.risk_counts.Medium}</div>
              <div className="bg-green-100 p-2 rounded">Low<br />{doc.risk_counts.Low}</div>
              <div className="bg-slate-100 p-2 rounded">Total<br />{doc.total_risks}</div>
            </div>

            <p className="text-sm">
              <strong>Acquisition Risk Index:</strong>{" "}
              {doc.acquisition_risk_index ?? 0}
            </p>
          </div>
        ))}
      </div>

      {/* ================= HEAT MAP ================= */}
      <div className="max-w-5xl mx-auto space-y-3">
        {ddSummary.heat_map.map((risk, i) => (
          <div
            key={i}
            className={`border-l-4 p-4 rounded-md ${severityColor(
              risk.severity
            )}`}
          >
            <p className="font-semibold">
              📄 {risk.document} — {risk.risk_type} (Page {risk.page})
            </p>
            <p className="italic text-sm text-slate-700">
              “{risk.snippet}”
            </p>
          </div>
        ))}
      </div>

      {/* ================= FLAGS ================= */}
      {flags.length > 0 && (
        <div className="max-w-5xl mx-auto">
          <h2 className="text-lg font-bold text-red-600 mb-2">
            🚩 Critical Red Flags
          </h2>
          {flags.map((f, i) => (
            <div key={i} className="bg-red-50 border border-red-400 p-4 rounded-md mb-2">
              <p className="font-semibold">{f.document} (Page {f.page})</p>
              <p className="italic text-sm">“{f.snippet}”</p>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
