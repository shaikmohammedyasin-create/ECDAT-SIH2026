import React, { useEffect, useState } from "react";
import { Outlet } from "react-router-dom";
import { TopBar } from "./TopBar";
import { Sidebar } from "./Sidebar";
import { fetchDashboard } from "../services/api";

export const Layout: React.FC = () => {
  const [targetPath, setTargetPath] = useState<string>("test_corpus");
  const [scanStatus, setScanStatus] = useState<string>("Complete");
  const [cbomValid, setCbomValid] = useState<boolean>(true);

  useEffect(() => {
    fetchDashboard()
      .then((data) => {
        if (data.target_path) setTargetPath(data.target_path);
        if (data.status) setScanStatus(data.status);
        if (data.cbom_status) setCbomValid(data.cbom_status.valid);
      })
      .catch(() => {});
  }, []);

  return (
    <div className="bg-background text-on-surface flex flex-col h-screen w-screen overflow-hidden">
      <TopBar targetPath={targetPath} status={scanStatus} cbomValid={cbomValid} />
      <div className="flex flex-1 overflow-hidden">
        <Sidebar />
        <main className="flex-1 flex flex-col min-w-0 bg-surface overflow-y-auto">
          <Outlet />
        </main>
      </div>
    </div>
  );
};
