import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { adminAPI } from '../../utils/api';
import { Button, Card, LoadingSpinner } from '../../components/FormComponents';
import toast from 'react-hot-toast';

const ImportProducts = () => {
  const [file, setFile] = useState(null);
  const [uploading, setUploading] = useState(false);
  const [preview, setPreview] = useState(null);
  const navigate = useNavigate();

  const handleFileChange = (e) => {
    const selectedFile = e.target.files[0];
    if (selectedFile) {
      // Check if it's a CSV file
      if (selectedFile.type !== 'text/csv' && !selectedFile.name.endsWith('.csv')) {
        toast.error('Please select a valid CSV file');
        return;
      }

      setFile(selectedFile);

      // Create preview
      const reader = new FileReader();
      reader.onload = (e) => {
        const csvContent = e.target.result;
        const lines = csvContent.split('\n').slice(0, 5); // Show first 5 lines
        setPreview(lines.join('\n'));
      };
      reader.readAsText(selectedFile);
    }
  };

  const handleUpload = async () => {
    if (!file) {
      toast.error('Please select a CSV file first');
      return;
    }

    setUploading(true);
    try {
      const response = await adminAPI.bulkUploadProducts(file);
      toast.success(`Successfully imported ${response.imported_count} products!`);
      navigate('/admin/products');
    } catch (error) {
      console.error('Upload error:', error);
      const errorMessage = error.response?.data?.error || 'Failed to upload CSV file';
      toast.error(errorMessage);
    } finally {
      setUploading(false);
    }
  };

  const downloadTemplate = () => {
    const template = `name,sku,brand,category,description,price,stock_quantity,minimum_order_value,image_url,is_active
Sample Product,SKU001,Sample Brand,Electronics,This is a sample product description,99.99,100,10.00,https://example.com/image.jpg,true
Another Product,,Another Brand,All,Another product description,149.99,50,25.00,,false`;

    const blob = new Blob([template], { type: 'text/csv' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'products_template.csv';
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    window.URL.revokeObjectURL(url);
  };

  return (
    <div className="max-w-4xl mx-auto">
      {/* Header */}
      <div className="mb-8">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">Import Products</h1>
            <p className="mt-2 text-gray-600">
              Upload a CSV file to bulk import products
            </p>
          </div>
          <Button
            variant="outline"
            onClick={() => navigate('/admin/products')}
          >
            Back to Products
          </Button>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        {/* Upload Section */}
        <Card>
          <div className="p-6">
            <h2 className="text-xl font-semibold text-gray-900 mb-4">
              Upload CSV File
            </h2>

            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Select CSV File
                </label>
                <input
                  type="file"
                  accept=".csv"
                  onChange={handleFileChange}
                  className="block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-sm file:font-semibold file:bg-blue-50 file:text-blue-700 hover:file:bg-blue-100"
                />
              </div>

              {file && (
                <div className="p-4 bg-green-50 border border-green-200 rounded-lg">
                  <p className="text-sm text-green-800">
                    <strong>Selected file:</strong> {file.name}
                  </p>
                  <p className="text-sm text-green-600 mt-1">
                    Size: {(file.size / 1024).toFixed(2)} KB
                  </p>
                </div>
              )}

              <div className="flex space-x-3">
                <Button
                  onClick={handleUpload}
                  loading={uploading}
                  disabled={!file || uploading}
                  className="flex-1"
                >
                  {uploading ? 'Uploading...' : 'Upload Products'}
                </Button>
              </div>
            </div>
          </div>
        </Card>

        {/* Instructions Section */}
        <Card>
          <div className="p-6">
            <h2 className="text-xl font-semibold text-gray-900 mb-4">
              Instructions & Template
            </h2>

            <div className="space-y-4">
              <div>
                <h3 className="text-lg font-medium text-gray-900 mb-2">
                  CSV Format
                </h3>
                <p className="text-sm text-gray-600 mb-3">
                  Your CSV file should include the following columns:
                </p>
                <ul className="text-sm text-gray-600 space-y-1">
                  <li><strong>name:</strong> Product name (required)</li>
                  <li><strong>sku:</strong> Stock keeping unit (required)</li>
                  <li><strong>brand:</strong> Product brand (optional)</li>
                  <li><strong>category:</strong> Product category (optional)</li>
                  <li><strong>description:</strong> Product description (optional)</li>
                  <li><strong>price:</strong> Product price (required)</li>
                  <li><strong>stock_quantity:</strong> Available stock (required)</li>
                  <li><strong>minimum_order_value:</strong> Minimum order value (optional)</li>
                  <li><strong>image_url:</strong> Product image URL (optional)</li>
                  <li><strong>is_active:</strong> Product status (true/false, optional)</li>
                </ul>
              </div>

              <div>
                <Button
                  variant="outline"
                  onClick={downloadTemplate}
                  className="w-full"
                >
                  Download CSV Template
                </Button>
              </div>

              <div className="p-4 bg-yellow-50 border border-yellow-200 rounded-lg">
                <h4 className="text-sm font-medium text-yellow-800 mb-2">
                  Important Notes:
                </h4>
                <ul className="text-sm text-yellow-700 space-y-1">
                  <li>• First row should contain column headers</li>
                  <li>• Price and stock_quantity must be numbers</li>
                  <li>• is_active should be 'true' or 'false'</li>
                  <li>• SKU must be unique for each product</li>
                  <li>• Maximum file size: 5MB</li>
                </ul>
              </div>
            </div>
          </div>
        </Card>
      </div>

      {/* Preview Section */}
      {preview && (
        <Card className="mt-8">
          <div className="p-6">
            <h2 className="text-xl font-semibold text-gray-900 mb-4">
              File Preview (First 5 lines)
            </h2>
            <div className="bg-gray-50 p-4 rounded-lg">
              <pre className="text-sm text-gray-800 whitespace-pre-wrap font-mono">
                {preview}
              </pre>
            </div>
          </div>
        </Card>
      )}
    </div>
  );
};

export default ImportProducts;
