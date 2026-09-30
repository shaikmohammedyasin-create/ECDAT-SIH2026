import React from "react";
import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import { Layout } from "./components/Layout";

import Dashboard from "./pages/Dashboard";
import NewScan from "./pages/NewScan";
import Inventory from "./pages/Inventory";
import FindingInspector from "./pages/FindingInspector";
import MoscaSimulator from "./pages/Mosca";
import RiskAnalysis from "./pages/Risk";
import MigrationGuidance from "./pages/Migration";
import CBOMPage from "./pages/CBOM";
import TerminalPage from "./pages/Terminal";
import SettingsPage from "./pages/Settings";
import ReportsPage from "./pages/Reports";

export const App: React.FC = () => {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Layout />}>
          <Route index element={<Navigate to="/dashboard" replace />} />
          <Route path="dashboard" element={<Dashboard />} />
          <Route path="scan" element={<NewScan />} />
          <Route path="scan/new" element={<NewScan />} />
          <Route path="inventory" element={<Inventory />} />
          <Route path="findings/:id" element={<FindingInspector />} />
          <Route path="findings" element={<Navigate to="/findings/0" replace />} />
          <Route path="mosca" element={<MoscaSimulator />} />
          <Route path="risk" element={<RiskAnalysis />} />
          <Route path="migration" element={<MigrationGuidance />} />
          <Route path="cbom" element={<CBOMPage />} />
          <Route path="terminal" element={<TerminalPage />} />
          <Route path="settings" element={<SettingsPage />} />
          <Route path="reports" element={<ReportsPage />} />
          <Route path="*" element={<Navigate to="/dashboard" replace />} />
        </Route>
      </Routes>
    </BrowserRouter>
  );
};

export default App;
