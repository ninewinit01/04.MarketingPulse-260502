import { Navigate, Route, Routes } from "react-router-dom";

import { AdminLayout } from "@/components/AdminLayout";
import { Archive } from "@/pages/Archive";
import { Dashboard } from "@/pages/Dashboard";
import { IndustryDetail } from "@/pages/IndustryDetail";
import { ChannelsPage } from "@/pages/admin/ChannelsPage";
import { CollectionRunsPage } from "@/pages/admin/CollectionRunsPage";
import { IndustriesPage } from "@/pages/admin/IndustriesPage";
import { KeywordsPage } from "@/pages/admin/KeywordsPage";
import { SourcesPage } from "@/pages/admin/SourcesPage";

export default function App() {
  return (
    <Routes>
      <Route path="/" element={<Dashboard />} />
      <Route path="/archive" element={<Archive />} />
      <Route path="/industries/:slug" element={<IndustryDetail />} />
      <Route path="/admin" element={<AdminLayout />}>
        <Route index element={<Navigate to="/admin/industries" replace />} />
        <Route path="industries" element={<IndustriesPage />} />
        <Route path="keywords" element={<KeywordsPage />} />
        <Route path="sources" element={<SourcesPage />} />
        <Route path="channels" element={<ChannelsPage />} />
        <Route path="runs" element={<CollectionRunsPage />} />
      </Route>
    </Routes>
  );
}
