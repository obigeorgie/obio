import { useEffect, useState } from "react";
import { api } from "../api";
import { Link } from "react-router-dom";
import { Plus, User, Download } from "lucide-react";

export default function Learners() {
  const [learners, setLearners] = useState<any[]>([]);
  const [showForm, setShowForm] = useState(false);
  const [formData, setFormData] = useState({ learner_id: "", name: "", age: "", grade: "", notes: "" });
  const [loading, setLoading] = useState(true);
  const [exporting, setExporting] = useState(false);

  useEffect(() => {
    loadLearners();
  }, []);

  async function loadLearners() {
    try {
      const data = await api.listLearners();
      setLearners(data.learners || []);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  }

  async function handleExport(format: "json" | "csv") {
    setExporting(true);
    try {
      const data = await api.exportData({ format, learner_ids: learners.map((l) => l.id) });
      if (format === "csv" && data.data) {
        const blob = new Blob([data.data], { type: "text/csv" });
        const url = URL.createObjectURL(blob);
        const a = document.createElement("a");
        a.href = url;
        a.download = `obio-export-${new Date().toISOString().split("T")[0]}.csv`;
        a.click();
        URL.revokeObjectURL(url);
      } else {
        const blob = new Blob([JSON.stringify(data.learners, null, 2)], { type: "application/json" });
        const url = URL.createObjectURL(blob);
        const a = document.createElement("a");
        a.href = url;
        a.download = `obio-export-${new Date().toISOString().split("T")[0]}.json`;
        a.click();
        URL.revokeObjectURL(url);
      }
    } catch (e: any) {
      alert(e.message);
    } finally {
      setExporting(false);
    }
  }

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    try {
      await api.createLearner({
        learner_id: formData.learner_id,
        name: formData.name,
        age: formData.age ? parseInt(formData.age) : undefined,
        grade: formData.grade || undefined,
        notes: formData.notes,
      });
      setShowForm(false);
      setFormData({ learner_id: "", name: "", age: "", grade: "", notes: "" });
      loadLearners();
    } catch (e: any) {
      alert(e.message);
    }
  }

  return (
    <div>
      <div className="flex justify-between items-center mb-6">
        <h2 className="text-2xl font-bold">Learners</h2>
        <div className="flex gap-2">
          {learners.length > 0 && (
            <div className="flex gap-2">
              <button
                onClick={() => handleExport("csv")}
                disabled={exporting}
                className="flex items-center gap-2 bg-gray-100 text-gray-700 px-4 py-2 rounded-lg hover:bg-gray-200 disabled:opacity-50"
              >
                <Download className="w-4 h-4" />
                CSV
              </button>
              <button
                onClick={() => handleExport("json")}
                disabled={exporting}
                className="flex items-center gap-2 bg-gray-100 text-gray-700 px-4 py-2 rounded-lg hover:bg-gray-200 disabled:opacity-50"
              >
                <Download className="w-4 h-4" />
                JSON
              </button>
            </div>
          )}
          <button
            onClick={() => setShowForm(!showForm)}
            className="flex items-center gap-2 bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700"
          >
            <Plus className="w-4 h-4" />
            Add Learner
          </button>
        </div>
      </div>

      {showForm && (
        <form onSubmit={handleSubmit} className="bg-white rounded-lg border p-6 mb-6 space-y-4">
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium mb-1">Learner ID *</label>
              <input
                required
                className="w-full border rounded-lg px-3 py-2"
                value={formData.learner_id}
                onChange={(e) => setFormData({ ...formData, learner_id: e.target.value })}
                placeholder="e.g., child-001"
              />
            </div>
            <div>
              <label className="block text-sm font-medium mb-1">Name</label>
              <input
                className="w-full border rounded-lg px-3 py-2"
                value={formData.name}
                onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                placeholder="Child's name"
              />
            </div>
            <div>
              <label className="block text-sm font-medium mb-1">Age</label>
              <input
                type="number"
                className="w-full border rounded-lg px-3 py-2"
                value={formData.age}
                onChange={(e) => setFormData({ ...formData, age: e.target.value })}
                placeholder="e.g., 7"
              />
            </div>
            <div>
              <label className="block text-sm font-medium mb-1">Grade</label>
              <input
                className="w-full border rounded-lg px-3 py-2"
                value={formData.grade}
                onChange={(e) => setFormData({ ...formData, grade: e.target.value })}
                placeholder="e.g., 2nd"
              />
            </div>
          </div>
          <div>
            <label className="block text-sm font-medium mb-1">Notes</label>
            <textarea
              className="w-full border rounded-lg px-3 py-2"
              rows={2}
              value={formData.notes}
              onChange={(e) => setFormData({ ...formData, notes: e.target.value })}
            />
          </div>
          <div className="flex gap-2">
            <button type="submit" className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700">
              Create Learner
            </button>
            <button type="button" onClick={() => setShowForm(false)} className="text-gray-600 px-4 py-2">
              Cancel
            </button>
          </div>
        </form>
      )}

      {loading ? (
        <div className="text-gray-500">Loading...</div>
      ) : learners.length === 0 ? (
        <div className="text-gray-500 text-center py-12">No learners yet. Add one to get started.</div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {learners.map((l: any) => (
            <Link
              key={l.id}
              to={`/learners/${l.id}`}
              className="bg-white rounded-lg border p-4 hover:shadow-md transition-shadow"
            >
              <div className="flex items-center gap-3 mb-2">
                <div className="p-2 bg-blue-50 rounded-full">
                  <User className="w-5 h-5 text-blue-600" />
                </div>
                <div>
                  <div className="font-semibold text-gray-900">{l.name || l.id}</div>
                  <div className="text-sm text-gray-500">ID: {l.id}</div>
                </div>
              </div>
              <div className="text-sm text-gray-600">
                {l.age && `Age: ${l.age}`} {l.grade && `• Grade: ${l.grade}`}
              </div>
            </Link>
          ))}
        </div>
      )}
    </div>
  );
}
