import './ClassOverviewModal.css';
import { useEffect, useState } from 'react';
import api from '../api/axiosConfig';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';

export function ClassOverviewModal({ isOpen, onClose }) {
    const [data, setData] = useState([]);
    const [isLoading, setIsLoading] = useState(false);
    const [error, setError] = useState('');

    const getBarColor = (val) => {
        if (val < 40) return 'rgb(239, 68, 68)';
        if (val < 70) return 'rgb(245, 158, 11)';
        return 'rgb(34, 197, 94)';
    };

    useEffect(() => {
        const fetchOverview = async () => {
            setIsLoading(true);
            setError('');
            try {
                const response = await api.get('/statistics/class-overview');
                const rawTopics = response.data.topics || [];

                const formatted = rawTopics.map((t) => {
                    const rawVal = Number(t.average_mastery) || 0;
                    const percentage = rawVal * 100;
                    const rounded = Number(percentage.toFixed(1));
                    return {
                        ...t,
                        displayMastery: rounded,
                        fill: getBarColor(rounded)
                    };
                });

                setData(formatted);
            } catch (error) {
                console.error("Σφάλμα κατά τη φόρτωση στατιστικών:", error);
                setError("Αδυναμία φόρτωσης των στατιστικών της τάξης.")
            } finally {
                setIsLoading(false);
            }
        };

        if (isOpen) {
            fetchOverview();
        }
    }, [isOpen]);

    if (!isOpen) return null;

    const weakestTopic = data.length
        ? [...data].sort((a, b) => a.displayMastery - b.displayMastery)[0]
        : null;

    const strongestTopic = data.length
        ? [...data].sort((a, b) => b.displayMastery - a.displayMastery)[0]
        : null;


    return (
        <div className="modal-overlay" onClick={onClose}>
            <div className="modal-content overview-modal-content" onClick={(e) => e.stopPropagation()}>
                <div className="modal-header">
                    <h2>Επισκόπηση Τάξης</h2>
                    <button className="modal-close-btn" onClick={onClose}>
                        &#10005;
                    </button>
                </div>

                {isLoading ? (
                    <div className="overview-status">Φόρτωση δεδομένων τάξης...</div>
                ) : error ? (
                    <div className="overview-error">{error}</div>
                ) : data.length === 0 ? (
                    <div className="overview-status">Δεν υπάρχουν διαθέσιμα κεφάλαια ή δεδομένα φοιτητών.</div>
                ) : (
                    <>
                        <div className="overview-summary-cards">
                            {strongestTopic && (
                                <div className="summary-card">
                                    <span className="summary-label">Δυνατότερο Κεφάλαιο</span>
                                    <strong className="summary-value text-green">
                                        {strongestTopic.topic_name} ({strongestTopic.displayMastery}%)
                                    </strong>
                                </div>
                            )}
                            {weakestTopic && (
                                <div className="summary-card">
                                    <span className="summary-label">Αδύναμο Κεφάλαιο</span>
                                    <strong className="summary-value text-red">
                                        {weakestTopic.topic_name} ({weakestTopic.displayMastery}%)
                                    </strong>
                                </div>
                            )}
                        </div>

                        <div className="chart-wrapper">
                            <ResponsiveContainer width="100%" height={340}>
                                <BarChart
                                    layout="vertical"
                                    data={data}
                                    margin={{ top: 10, right: 30, left: 10, bottom: 10 }}
                                >
                                    <CartesianGrid strokeDasharray="3 3" stroke="rgb(50, 50, 50)" horizontal={false} />
                                    <XAxis
                                        type="number"
                                        domain={[0, 100]}
                                        stroke="rgb(170, 170, 170)"
                                        tick={{ fill: 'rgb(210, 210, 210)', fontSize: 12 }}
                                        unit="%"
                                    />
                                    <YAxis
                                        type="category"
                                        dataKey="topic_name"
                                        width={175}
                                        stroke="rgb(170, 170, 170)"
                                        tick={{ fill: 'rgb(210, 210, 210)', fontSize: 12 }}
                                        interval={0}
                                    />
                                    <Tooltip
                                        cursor={{ fill: 'rgba(255, 255, 255, 0.05)' }}
                                        contentStyle={{
                                            backgroundColor: 'rgb(24, 24, 24)',
                                            border: '1px solid rgb(65, 65, 65)',
                                            borderRadius: '8px'
                                        }}
                                        labelStyle={{ fontWeight: 'bold', marginBottom: '4px', color: 'rgb(96, 165, 250)' }}
                                        itemStyle={{ color: 'rgb(240, 240, 240)' }}
                                        formatter={(value) => [`${value}%`, 'Μέσο Mastery']}
                                    />
                                    <Bar dataKey="displayMastery" radius={[0, 6, 6, 0]} maxBarSize={26} />
                                </BarChart>
                            </ResponsiveContainer>
                        </div>

                        <div className="chart-legend">
                            <span className="legend-item">
                                <span className="legend-dot dot-red"></span> &lt; 40% (Χρειάζεται ενίσχυση)
                            </span>
                            <span className="legend-item">
                                <span className="legend-dot dot-orange"></span> 40% - 69% (Ικανοποιητικό)
                            </span>
                            <span className="legend-item">
                                <span className="legend-dot dot-green"></span> &ge; 70% (Άριστη κατανόηση)
                            </span>
                        </div>
                    </>
                )}
            </div>
        </div>
    );
}