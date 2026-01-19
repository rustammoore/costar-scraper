import React, { useState, useEffect, useCallback } from 'react';
import axios from 'axios';
import './App.css';

const API_URL = process.env.REACT_APP_BACKEND_URL || '';

// Property Card Component
const PropertyCard = ({ property }) => {
  const [imageError, setImageError] = useState(false);
  
  const formatPrice = (price) => {
    if (!price) return 'Price Not Disclosed';
    return price;
  };

  const getPropertyTypeColor = (type) => {
    const colors = {
      'Office': 'bg-blue-100 text-blue-800',
      'Retail': 'bg-green-100 text-green-800',
      'Industrial': 'bg-orange-100 text-orange-800',
      'Warehouse': 'bg-yellow-100 text-yellow-800',
      'Commercial Land': 'bg-purple-100 text-purple-800',
      'Commercial Vacant Land': 'bg-purple-100 text-purple-800',
      'Industrial Land': 'bg-amber-100 text-amber-800',
      'Fast Food': 'bg-red-100 text-red-800',
      'Drug Store': 'bg-teal-100 text-teal-800',
      'Flex': 'bg-indigo-100 text-indigo-800',
      'Light Manufacturing': 'bg-slate-100 text-slate-800',
    };
    return colors[type] || 'bg-gray-100 text-gray-800';
  };

  const placeholderImage = 'https://images.unsplash.com/photo-1486406146926-c627a92ad1ab?w=400&h=300&fit=crop';

  return (
    <div 
      className="property-card bg-white rounded-xl shadow-md overflow-hidden transition-all duration-300 hover:shadow-xl"
      data-testid={`property-card-${property.costar_id}`}
    >
      {/* Property Image */}
      <div className="relative h-48 bg-gray-200">
        <img
          src={imageError ? placeholderImage : (property.image_url || placeholderImage)}
          alt={property.address}
          className="w-full h-full object-cover"
          onError={() => setImageError(true)}
        />
        {property.property_type && (
          <span className={`absolute top-3 left-3 px-3 py-1 rounded-full text-xs font-medium ${getPropertyTypeColor(property.property_type)}`}>
            {property.property_type}
          </span>
        )}
        {property.cap_rate && (
          <span className="absolute top-3 right-3 px-3 py-1 rounded-full text-xs font-medium bg-green-500 text-white">
            {property.cap_rate} Cap
          </span>
        )}
      </div>

      {/* Property Details */}
      <div className="p-5">
        {/* Price */}
        <div className="mb-3">
          <span className="text-2xl font-bold text-gray-900">
            {formatPrice(property.price)}
          </span>
          {property.price_per_sf && (
            <span className="ml-2 text-sm text-gray-500">
              ({property.price_per_sf})
            </span>
          )}
        </div>

        {/* Address */}
        <h3 className="text-lg font-semibold text-gray-800 mb-1">
          {property.address}
        </h3>
        <p className="text-gray-600 mb-3">
          {property.city}, {property.state} {property.zip_code}
        </p>

        {/* Property Stats */}
        <div className="flex flex-wrap gap-3 text-sm text-gray-600">
          {property.square_feet && (
            <div className="flex items-center gap-1">
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M4 8V4m0 0h4M4 4l5 5m11-1V4m0 0h-4m4 0l-5 5M4 16v4m0 0h4m-4 0l5-5m11 5v-4m0 4h-4m4 0l-5-5" />
              </svg>
              <span>{property.square_feet} SF</span>
            </div>
          )}
          {property.year_built && (
            <div className="flex items-center gap-1">
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
              </svg>
              <span>Built {property.year_built}</span>
            </div>
          )}
        </div>

        {/* Search Name Badge */}
        {property.search_name && (
          <div className="mt-4 pt-4 border-t border-gray-100">
            <span className="text-xs text-gray-500">Search: </span>
            <span className="text-xs font-medium text-gray-700">{property.search_name}</span>
          </div>
        )}
      </div>
    </div>
  );
};

// Filter Component
const Filters = ({ filters, setFilters, states, propertyTypes }) => {
  return (
    <div className="bg-white rounded-xl shadow-md p-6 mb-8" data-testid="filters-section">
      <h3 className="text-lg font-semibold text-gray-800 mb-4">Filter Properties</h3>
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        {/* City Search */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">City</label>
          <input
            type="text"
            placeholder="Search city..."
            value={filters.city}
            onChange={(e) => setFilters({ ...filters, city: e.target.value })}
            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            data-testid="filter-city-input"
          />
        </div>

        {/* State Select */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">State</label>
          <select
            value={filters.state}
            onChange={(e) => setFilters({ ...filters, state: e.target.value })}
            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            data-testid="filter-state-select"
          >
            <option value="">All States</option>
            {states.map(state => (
              <option key={state} value={state}>{state}</option>
            ))}
          </select>
        </div>

        {/* Property Type Select */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">Property Type</label>
          <select
            value={filters.property_type}
            onChange={(e) => setFilters({ ...filters, property_type: e.target.value })}
            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            data-testid="filter-type-select"
          >
            <option value="">All Types</option>
            {propertyTypes.map(type => (
              <option key={type} value={type}>{type}</option>
            ))}
          </select>
        </div>

        {/* Clear Filters */}
        <div className="flex items-end">
          <button
            onClick={() => setFilters({ city: '', state: '', property_type: '' })}
            className="w-full px-4 py-2 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 transition-colors font-medium"
            data-testid="clear-filters-btn"
          >
            Clear Filters
          </button>
        </div>
      </div>
    </div>
  );
};

// Loading Skeleton
const LoadingSkeleton = () => (
  <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
    {[...Array(8)].map((_, i) => (
      <div key={i} className="bg-white rounded-xl shadow-md overflow-hidden">
        <div className="h-48 loading-skeleton"></div>
        <div className="p-5">
          <div className="h-8 loading-skeleton rounded mb-3"></div>
          <div className="h-5 loading-skeleton rounded mb-2"></div>
          <div className="h-4 loading-skeleton rounded w-3/4"></div>
        </div>
      </div>
    ))}
  </div>
);

// Main App Component
function App() {
  const [properties, setProperties] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [stats, setStats] = useState({ total_properties: 0, by_state: {}, by_type: {} });
  const [syncStatus, setSyncStatus] = useState({ configured: false, message: '' });
  const [syncing, setSyncing] = useState(false);
  const [seeding, setSeeding] = useState(false);
  const [filters, setFilters] = useState({ city: '', state: '', property_type: '' });

  // Fetch properties
  const fetchProperties = useCallback(async () => {
    try {
      setLoading(true);
      const params = new URLSearchParams();
      if (filters.city) params.append('city', filters.city);
      if (filters.state) params.append('state', filters.state);
      if (filters.property_type) params.append('property_type', filters.property_type);
      params.append('limit', '100');

      const response = await axios.get(`${API_URL}/api/properties?${params}`);
      setProperties(response.data.properties);
      setError(null);
    } catch (err) {
      console.error('Error fetching properties:', err);
      setError('Failed to load properties. Please try again.');
    } finally {
      setLoading(false);
    }
  }, [filters]);

  // Fetch stats
  const fetchStats = async () => {
    try {
      const response = await axios.get(`${API_URL}/api/properties/stats`);
      setStats(response.data);
    } catch (err) {
      console.error('Error fetching stats:', err);
    }
  };

  // Check sync status
  const checkSyncStatus = async () => {
    try {
      const response = await axios.get(`${API_URL}/api/sync-status`);
      setSyncStatus(response.data);
    } catch (err) {
      console.error('Error checking sync status:', err);
    }
  };

  // Sync emails
  const handleSync = async () => {
    if (syncing) return;
    setSyncing(true);
    try {
      const response = await axios.post(`${API_URL}/api/sync-emails?days_back=30&max_emails=100`);
      alert(`Sync complete! Found ${response.data.total_found} properties, added ${response.data.new_added} new.`);
      fetchProperties();
      fetchStats();
    } catch (err) {
      alert(err.response?.data?.detail || 'Sync failed. Please check Gmail credentials.');
    } finally {
      setSyncing(false);
    }
  };

  // Seed sample data
  const handleSeedSample = async () => {
    if (seeding) return;
    setSeeding(true);
    try {
      const response = await axios.post(`${API_URL}/api/seed-sample`);
      alert(`Added ${response.data.properties_added} sample properties!`);
      fetchProperties();
      fetchStats();
    } catch (err) {
      alert('Failed to seed sample data.');
    } finally {
      setSeeding(false);
    }
  };

  useEffect(() => {
    fetchProperties();
    fetchStats();
    checkSyncStatus();
  }, [fetchProperties]);

  // Extract unique states and property types from stats
  const states = Object.keys(stats.by_state).sort();
  const propertyTypes = Object.keys(stats.by_type).sort();

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-blue-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
            <div>
              <h1 className="text-3xl font-bold text-gray-900" data-testid="app-title">
                CoStar Property Gallery
              </h1>
              <p className="text-gray-600 mt-1">
                Commercial Real Estate Listings from Email Alerts
              </p>
            </div>
            <div className="flex gap-3">
              {/* Seed Sample Button */}
              <button
                onClick={handleSeedSample}
                disabled={seeding}
                className="px-5 py-2.5 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors font-medium disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
                data-testid="seed-sample-btn"
              >
                {seeding ? (
                  <>
                    <svg className="animate-spin h-4 w-4" viewBox="0 0 24 24">
                      <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none"></circle>
                      <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                    </svg>
                    Adding...
                  </>
                ) : (
                  <>
                    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 6v6m0 0v6m0-6h6m-6 0H6" />
                    </svg>
                    Add Sample Data
                  </>
                )}
              </button>
              {/* Sync Button */}
              <button
                onClick={handleSync}
                disabled={syncing || !syncStatus.configured}
                className="px-5 py-2.5 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors font-medium disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
                data-testid="sync-emails-btn"
              >
                {syncing ? (
                  <>
                    <svg className="animate-spin h-4 w-4" viewBox="0 0 24 24">
                      <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none"></circle>
                      <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                    </svg>
                    Syncing...
                  </>
                ) : (
                  <>
                    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
                    </svg>
                    Sync from Gmail
                  </>
                )}
              </button>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Stats Summary */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
          <div className="bg-white rounded-xl shadow-md p-5" data-testid="stat-total">
            <p className="text-sm text-gray-600 mb-1">Total Properties</p>
            <p className="text-3xl font-bold text-gray-900">{stats.total_properties}</p>
          </div>
          <div className="bg-white rounded-xl shadow-md p-5" data-testid="stat-states">
            <p className="text-sm text-gray-600 mb-1">States</p>
            <p className="text-3xl font-bold text-blue-600">{states.length}</p>
          </div>
          <div className="bg-white rounded-xl shadow-md p-5" data-testid="stat-types">
            <p className="text-sm text-gray-600 mb-1">Property Types</p>
            <p className="text-3xl font-bold text-green-600">{propertyTypes.length}</p>
          </div>
          <div className="bg-white rounded-xl shadow-md p-5" data-testid="stat-sync">
            <p className="text-sm text-gray-600 mb-1">Gmail Sync</p>
            <p className={`text-lg font-bold ${syncStatus.configured ? 'text-green-600' : 'text-orange-500'}`}>
              {syncStatus.configured ? 'Ready' : 'Not Configured'}
            </p>
          </div>
        </div>

        {/* Sync Status Alert */}
        {!syncStatus.configured && (
          <div className="bg-amber-50 border-l-4 border-amber-400 p-4 mb-8 rounded-r-lg" data-testid="sync-alert">
            <div className="flex">
              <div className="flex-shrink-0">
                <svg className="h-5 w-5 text-amber-400" viewBox="0 0 20 20" fill="currentColor">
                  <path fillRule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
                </svg>
              </div>
              <div className="ml-3">
                <p className="text-sm text-amber-700">
                  <strong>Gmail Sync Not Configured:</strong> {syncStatus.message}
                </p>
                <p className="text-sm text-amber-600 mt-1">
                  Use the "Add Sample Data" button to add demo properties, or configure Gmail API credentials to sync real emails.
                </p>
              </div>
            </div>
          </div>
        )}

        {/* Filters */}
        {stats.total_properties > 0 && (
          <Filters
            filters={filters}
            setFilters={setFilters}
            states={states}
            propertyTypes={propertyTypes}
          />
        )}

        {/* Properties Grid */}
        {loading ? (
          <LoadingSkeleton />
        ) : error ? (
          <div className="text-center py-12">
            <div className="text-red-500 text-lg mb-4">{error}</div>
            <button
              onClick={fetchProperties}
              className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
              data-testid="retry-btn"
            >
              Retry
            </button>
          </div>
        ) : properties.length === 0 ? (
          <div className="text-center py-16 bg-white rounded-xl shadow-md" data-testid="empty-state">
            <svg className="mx-auto h-16 w-16 text-gray-400 mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="1.5" d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4" />
            </svg>
            <h3 className="text-xl font-semibold text-gray-800 mb-2">No Properties Found</h3>
            <p className="text-gray-600 mb-6 max-w-md mx-auto">
              {filters.city || filters.state || filters.property_type
                ? 'No properties match your filters. Try adjusting your search criteria.'
                : 'Get started by adding sample data or syncing emails from CoStar.'}
            </p>
            <div className="flex justify-center gap-3">
              {(filters.city || filters.state || filters.property_type) && (
                <button
                  onClick={() => setFilters({ city: '', state: '', property_type: '' })}
                  className="px-6 py-2 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 font-medium"
                  data-testid="clear-filters-empty-btn"
                >
                  Clear Filters
                </button>
              )}
              <button
                onClick={handleSeedSample}
                disabled={seeding}
                className="px-6 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 font-medium disabled:opacity-50"
                data-testid="seed-empty-btn"
              >
                Add Sample Data
              </button>
            </div>
          </div>
        ) : (
          <>
            <div className="flex items-center justify-between mb-6">
              <p className="text-gray-600" data-testid="results-count">
                Showing <span className="font-semibold text-gray-900">{properties.length}</span> properties
              </p>
            </div>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6" data-testid="properties-grid">
              {properties.map((property, index) => (
                <div key={property.costar_id || index} className="animate-fadeIn" style={{ animationDelay: `${index * 50}ms` }}>
                  <PropertyCard property={property} />
                </div>
              ))}
            </div>
          </>
        )}
      </main>

      {/* Footer */}
      <footer className="bg-white border-t border-gray-200 mt-12">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <p className="text-center text-gray-500 text-sm">
            CoStar Property Gallery • Data sourced from CoStar Daily Alert emails
          </p>
        </div>
      </footer>
    </div>
  );
}

export default App;
