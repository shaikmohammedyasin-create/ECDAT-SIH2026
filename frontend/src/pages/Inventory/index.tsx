import React, { useEffect, useState, useCallback } from "react";
import { useNavigate } from "react-router-dom";
import { fetchInventory } from "../../services/api";
import type { InventoryResponse } from "../../types";

export const InventoryPage: React.FC = () => {
  const navigate = useNavigate();
  const [data, setData] = useState<InventoryResponse | null>(null);
  const [search, setSearch] = useState<string>("");
  const [algorithm, setAlgorithm] = useState<string>("All");
  const [quantumStatus, setQuantumStatus] = useState<string>("All");
  const [threat, setThreat] = useState<string>("All");
  const [riskBand, setRiskBand] = useState<string>("All");
  const [page, setPage] = useState<number>(1);
  const [loading, setLoading] = useState<boolean>(true);

  const loadInventory = useCallback(() => {
    fetchInventory({
      search,
      algorithm,
      quantum_status: quantumStatus,
      threat,
      risk_band: riskBand,
      page,
      page_size: 50,
    })
      .then((res) => {
        setData(res);
        setLoading(false);
      })
      .catch(() => setLoading(false));
  }, [search, algorithm, quantumStatus, threat, riskBand, page]);

  useEffect(() => {
    loadInventory();
  }, [loadInventory]);

  const handleSearchSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setPage(1);
    loadInventory();
  };

  const bandColors: Record<string, string> = {
    Critical: "bg-red-800 text-white border-red-600",
    High: "bg-orange-800 text-white border-orange-600",
    Medium: "bg-amber-800 text-white border-amber-600",
    Low: "bg-green-800 text-white border-green-600",
    Info: "bg-slate-800 text-slate-300 border-slate-600",
  };

  return (
    <div className="flex-1 p-3 sm:p-4 md:p-6 space-y-4">
      {/* Header Banner */}
      <section className="flex flex-col md:flex-row md:items-end justify-between border-b border-outline-variant pb-3 gap-2">
        <div>
          <div className="flex items-center gap-2 flex-wrap">
            <h1 className="text-lg sm:text-xl font-bold tracking-tight text-on-surface">Cryptographic Asset Inventory</h1>
            <span className="px-1.5 py-0.5 rounded bg-primary-container/15 border border-primary-container/40 text-primary font-mono text-[10px] uppercase font-semibold">
              NORMALIZED CBOM VIEW
            </span>
          </div>
          <p className="text-xs text-on-surface-variant mt-1 font-sans">
            Normalized Bill of Cryptographic Materials (CBOM) with Quantum Risk Classification and Evidence Provenance
          </p>
        </div>
        <div className="text-xs font-mono text-outline">
          Total Discovered: <span className="text-tertiary font-bold">{data?.total ?? 0}</span>
        </div>
      </section>

      {/* Filter Toolbar matching Stitch */}
      <section className="bg-surface-container-low border border-outline-variant rounded p-3">
        <form onSubmit={handleSearchSubmit} className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-6 gap-2">
          <div className="sm:col-span-2">
            <div className="relative flex items-center">
              <span className="material-symbols-outlined absolute left-2 text-outline text-xs">search</span>
              <input
                type="text"
                placeholder="Search symbol, cipher, rule ID..."
                value={search}
                onChange={(e) => setSearch(e.target.value)}
                className="w-full bg-surface-container-lowest text-on-surface font-mono text-xs pl-7 pr-2 py-1.5 rounded border border-outline-variant focus:outline-none focus:border-primary"
              />
            </div>
          </div>

          <div>
            <select
              value={algorithm}
              onChange={(e) => {
                setAlgorithm(e.target.value);
                setPage(1);
              }}
              className="w-full bg-surface-container-lowest text-on-surface font-mono text-xs px-2 py-1.5 rounded border border-outline-variant focus:outline-none focus:border-primary"
            >
              <option value="All">All Algorithms</option>
              {data?.algorithms.map((a) => (
                <option key={a} value={a}>
                  {a}
                </option>
              ))}
            </select>
          </div>

          <div>
            <select
              value={quantumStatus}
              onChange={(e) => {
                setQuantumStatus(e.target.value);
                setPage(1);
              }}
              className="w-full bg-surface-container-lowest text-on-surface font-mono text-xs px-2 py-1.5 rounded border border-outline-variant focus:outline-none focus:border-primary"
            >
              <option value="All">All Quantum Status</option>
              {data?.quantum_classes.map((q) => (
                <option key={q} value={q}>
                  {q}
                </option>
              ))}
            </select>
          </div>

          <div>
            <select
              value={threat}
              onChange={(e) => {
                setThreat(e.target.value);
                setPage(1);
              }}
              className="w-full bg-surface-container-lowest text-on-surface font-mono text-xs px-2 py-1.5 rounded border border-outline-variant focus:outline-none focus:border-primary"
            >
              <option value="All">All Threats</option>
              <option value="HNDL">HNDL</option>
              <option value="TNFL">TNFL</option>
              <option value="None">None</option>
            </select>
          </div>

          <div>
            <select
              value={riskBand}
              onChange={(e) => {
                setRiskBand(e.target.value);
                setPage(1);
              }}
              className="w-full bg-surface-container-lowest text-on-surface font-mono text-xs px-2 py-1.5 rounded border border-outline-variant focus:outline-none focus:border-primary"
            >
              <option value="All">All Risk Bands</option>
              <option value="Critical">Critical</option>
              <option value="High">High</option>
              <option value="Medium">Medium</option>
              <option value="Low">Low</option>
            </select>
          </div>
        </form>
      </section>

      {/* Main Table */}
      <section className="bg-surface-container-low border border-outline-variant rounded overflow-hidden">
        {loading ? (
          <div className="p-8 text-center font-mono text-xs text-outline">Loading cryptographic inventory...</div>
        ) : !data || data.items.length === 0 ? (
          <div className="p-8 text-center font-mono text-xs text-outline">No cryptographic assets match the selected filters.</div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full font-mono text-xs text-left">
              <thead>
                <tr className="border-b border-outline-variant bg-surface-container-lowest text-outline">
                  <th className="py-2 px-3">Rule ID</th>
                  <th className="py-2 px-3">Algorithm</th>
                  <th className="py-2 px-3">Primitive</th>
                  <th className="py-2 px-3">Key Size</th>
                  <th className="py-2 px-3">Usage</th>
                  <th className="py-2 px-3">Quantum Status</th>
                  <th className="py-2 px-3">Threat</th>
                  <th className="py-2 px-3">Risk</th>
                  <th className="py-2 px-3">Confidence</th>
                  <th className="py-2 px-3">Location</th>
                  <th className="py-2 px-3 text-right">Action</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-outline-variant">
                {data.items.map((item) => (
                  <tr key={item.id} className="hover:bg-surface-container transition-colors">
                    <td className="py-2 px-3 text-secondary font-semibold">{item.rule_id}</td>
                    <td className="py-2 px-3 font-bold text-on-surface">{item.algorithm}</td>
                    <td className="py-2 px-3 text-on-surface-variant">{item.primitive}</td>
                    <td className="py-2 px-3 text-outline">{item.key_size}</td>
                    <td className="py-2 px-3 text-primary">{item.usage}</td>
                    <td className="py-2 px-3">
                      <span
                        className={`px-1.5 py-0.2 rounded text-[10px] font-bold ${
                          item.quantum === "Vulnerable"
                            ? "bg-red-950 text-red-300 border border-red-700"
                            : item.quantum === "Weakened"
                            ? "bg-amber-950 text-amber-300 border border-amber-700"
                            : "bg-green-950 text-green-300 border border-green-700"
                        }`}
                      >
                        {item.quantum}
                      </span>
                    </td>
                    <td className="py-2 px-3">
                      {item.threat !== "None" ? (
                        <span className="px-1.5 py-0.2 rounded bg-red-900/60 border border-red-500 text-red-300 text-[10px] font-bold">
                          {item.threat}
                        </span>
                      ) : (
                        <span className="text-outline text-[10px]">None</span>
                      )}
                    </td>
                    <td className="py-2 px-3">
                      <span className={`px-1.5 py-0.2 rounded text-[10px] font-bold border ${bandColors[item.risk_band] || "bg-slate-700"}`}>
                        {item.risk_score}
                      </span>
                    </td>
                    <td className="py-2 px-3 text-tertiary">{item.confidence}</td>
                    <td className="py-2 px-3 text-on-surface-variant truncate max-w-xs" title={`${item.file_path}:${item.line}`}>
                      {item.file}:{item.line}
                    </td>
                    <td className="py-2 px-3 text-right">
                      <button
                        onClick={() => navigate(`/findings/${item.id}`)}
                        className="bg-surface-container-high hover:bg-surface-container-highest border border-outline-variant text-primary font-mono text-xs px-2 py-0.5 rounded transition-colors"
                      >
                        Inspect
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </section>
    </div>
  );
};

export default InventoryPage;
