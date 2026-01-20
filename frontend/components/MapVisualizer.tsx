import React, { memo, useMemo } from 'react';
import { ComposableMap, Geographies, Geography, ZoomableGroup } from "react-simple-maps";
import { Tooltip } from 'react-tooltip';
import Fuse from 'fuse.js';
import { DistrictData } from '@/services/api';

// Map of India TopoJSON
// Map of India TopoJSON
const INDIA_TOPO_JSON = "https://raw.githubusercontent.com/udit-001/india-maps-data/main/topojson/india.json";

interface MapVisualizerProps {
    districts: DistrictData[];
    selectedState: string | 'All';
    onDistrictClick?: (state: string) => void;
}

const MapVisualizer = ({ districts, selectedState, onDistrictClick }: MapVisualizerProps) => {

    // 1. Fuse.js for Fuzzy Matching
    // We index our current dataset so we can match TopoJSON names against it.
    const fuse = useMemo(() => {
        return new Fuse(districts, {
            keys: ['district'],
            threshold: 0.3, // Tolerance for typos
        });
    }, [districts]);

    // Create a fast lookup map after fuzzy matching or direct normalization
    const dataMap = useMemo(() => {
        const map: Record<string, DistrictData> = {};
        districts.forEach(d => {
            const key = d.district.toLowerCase().replace(/[^a-z0-9]/g, '');
            map[key] = d;
        });
        return map;
    }, [districts]);

    const findDistrictData = (topoName: string) => {
        if (!topoName) return null;

        // 1. Try Exact/Normalized match
        const key = topoName.toLowerCase().replace(/[^a-z0-9]/g, '');
        if (dataMap[key]) return dataMap[key];

        // 2. Try Fuzzy Match
        const results = fuse.search(topoName);
        if (results.length > 0) return results[0].item;

        return null;
    };

    // Internal state for position (zoom + center)
    const [position, setPosition] = React.useState({ coordinates: [78, 22] as [number, number], zoom: 1 });

    const handleZoomIn = () => {
        if (position.zoom >= 4) return;
        setPosition(pos => ({ ...pos, zoom: Math.min(pos.zoom * 1.5, 4) }));
    };

    const handleZoomOut = () => {
        if (position.zoom <= 1) return;
        setPosition(pos => ({ ...pos, zoom: Math.max(pos.zoom / 1.5, 1) }));
    };

    const handleReset = () => {
        setPosition({ coordinates: [78, 22], zoom: 1 });
        if (onDistrictClick) onDistrictClick('All');
    };

    return (
        <div className="bg-white p-6 rounded-xl shadow-sm border border-slate-200">
            <h3 className="text-lg font-semibold text-slate-800 mb-4 flex justify-between items-center">
                Geospatial Intelligence Map {selectedState !== 'All' && `(${selectedState})`}
                <span className="text-xs font-normal text-slate-500 bg-slate-100 px-2 py-1 rounded">Live Visualization</span>
            </h3>

            <div className="border border-slate-100 rounded-lg bg-slate-50 relative h-[500px] w-full overflow-hidden">
                {/* Manual Zoom Controls */}
                <div className="absolute top-4 right-4 flex flex-col gap-2 z-10">
                    <button
                        onClick={handleZoomIn}
                        className="bg-white p-2 rounded-md shadow-sm border border-slate-200 hover:bg-slate-50 text-slate-700 font-bold"
                        title="Zoom In"
                    >
                        +
                    </button>
                    <button
                        onClick={handleZoomOut}
                        className="bg-white p-2 rounded-md shadow-sm border border-slate-200 hover:bg-slate-50 text-slate-700 font-bold"
                        title="Zoom Out"
                    >
                        -
                    </button>
                    <button
                        onClick={handleReset}
                        className="bg-white p-2 text-xs rounded-md shadow-sm border border-slate-200 hover:bg-slate-50 text-slate-700 font-medium"
                        title="Reset View"
                    >
                        Reset
                    </button>
                </div>

                <ComposableMap
                    projection="geoMercator"
                    projectionConfig={{
                        scale: 1000,
                        center: [78, 22]
                    }}
                    width={800}
                    height={600}
                    style={{ width: "100%", height: "100%" }}
                >
                    <ZoomableGroup
                        zoom={position.zoom}
                        center={position.coordinates}
                        onMoveEnd={({ coordinates, zoom }) => setPosition({ coordinates: coordinates as [number, number], zoom })}
                        maxZoom={4}
                    >
                        <Geographies geography={INDIA_TOPO_JSON}>
                            {({ geographies }: { geographies: any[] }) =>
                                geographies.map((geo: any) => {
                                    // Robust property check for different TopoJSON formats
                                    const districtName = geo.properties.district || geo.properties.dtname || geo.properties.NAME_2 || geo.properties.name || "";
                                    const districtData = findDistrictData(districtName);

                                    // Filter Logic: If state is selected, dim others
                                    const isRelevantState = selectedState === 'All' || (districtData && districtData.state === selectedState);

                                    // Color Logic
                                    let fill = "#E2E8F0"; // Default
                                    let stroke = "#FFFFFF";

                                    if (districtData) {
                                        if (districtData.gap_percentage > 50) fill = "#EF4444"; // Red (Critical)
                                        else if (districtData.gap_percentage > 20) fill = "#F97316"; // Orange (Moderate)
                                        else if (districtData.gap_percentage > 0) fill = "#EAB308"; // Yellow (Emerging)
                                        else fill = "#10B981"; // Emerald (Compliant)
                                    }

                                    if (!isRelevantState) {
                                        fill = "#F1F5F9"; // Very light gray for non-selected states
                                        stroke = "#F8FAFC";
                                    }

                                    // Optimization: Don't render tooltip for filtered out states if in filter mode
                                    const tooltipContent = isRelevantState && districtData
                                        ? `${districtName}: ${districtData.gap_percentage}% Gap`
                                        : districtName;

                                    return (
                                        <Geography
                                            key={geo.rsmKey}
                                            geography={geo}
                                            fill={fill}
                                            stroke={stroke}
                                            strokeWidth={0.5}
                                            onClick={() => {
                                                if (districtData && onDistrictClick) {
                                                    onDistrictClick(districtData.state);
                                                }
                                            }}
                                            style={{
                                                default: { outline: "none" },
                                                hover: { fill: isRelevantState ? "#6366F1" : fill, outline: "none", cursor: 'pointer' },
                                                pressed: { outline: "none" },
                                            }}
                                            data-tooltip-id="map-tooltip"
                                            data-tooltip-content={tooltipContent}
                                        />
                                    );
                                })
                            }
                        </Geographies>
                    </ZoomableGroup>
                </ComposableMap>
                <Tooltip id="map-tooltip" />
            </div>

            <div className="flex gap-4 mt-4 text-xs text-slate-600 justify-center flex-wrap">
                <span className="flex items-center"><span className="w-3 h-3 bg-red-500 rounded-full mr-2"></span>Critical ({'>'}50%)</span>
                <span className="flex items-center"><span className="w-3 h-3 bg-orange-500 rounded-full mr-2"></span>Moderate (20-50%)</span>
                <span className="flex items-center"><span className="w-3 h-3 bg-yellow-400 rounded-full mr-2"></span>Emerging (1-20%)</span>
                <span className="flex items-center"><span className="w-3 h-3 bg-emerald-500 rounded-full mr-2"></span>Compliant (0%)</span>
            </div>
        </div>
    );
};

export default memo(MapVisualizer);
