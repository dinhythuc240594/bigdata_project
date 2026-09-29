import React, { useState } from 'react';
import { Play, Database, Terminal, RefreshCw, FileCode, CheckCircle2, XCircle } from 'lucide-react';

const QueryEditor = () => {
  const [engine, setEngine] = useState('hive');
  
  const templates = [
    { name: '1. Khởi tạo bảng Hive (Bắt buộc chạy đầu tiên)', engine: 'hive', query: "CREATE EXTERNAL TABLE IF NOT EXISTS laptop_products_common_hive (\n    brand STRING, category STRING, crawl_date STRING, discount DOUBLE, discount_rate DOUBLE, name STRING, original_price DOUBLE, price DOUBLE, product_id STRING, rating DOUBLE, sku STRING, sold INT, sold_info STRING, source STRING, url STRING\n) ROW FORMAT DELIMITED FIELDS TERMINATED BY '\\t' \nSTORED AS TEXTFILE LOCATION '/user/hadoopthuc/project/input_laptop_products_common';\n\nSHOW TABLES;" },
    { name: '2. Top 10 thương hiệu laptop nhiều sản phẩm nhất', engine: 'hive', query: 'SELECT brand, COUNT(*) as total_products FROM laptop_products_common_hive GROUP BY brand ORDER BY total_products DESC LIMIT 10;' },
    { name: '3. Thống kê giá bán trung bình theo thương hiệu', engine: 'hive', query: 'SELECT brand, ROUND(AVG(price), 0) as avg_price FROM laptop_products_common_hive WHERE price > 0 GROUP BY brand ORDER BY avg_price DESC LIMIT 10;' },
    { name: '4. Top 5 sản phẩm giảm giá (discount) sâu nhất', engine: 'hive', query: 'SELECT name, brand, original_price, price, discount_rate FROM laptop_products_common_hive WHERE discount_rate > 0 ORDER BY discount_rate DESC LIMIT 5;' },
    { name: '5. Điểm đánh giá (Rating) trung bình theo hãng', engine: 'hive', query: 'SELECT brand, ROUND(AVG(rating), 2) as avg_rating, sum(sold) as total_sold FROM laptop_products_common_hive WHERE rating > 0 GROUP BY brand ORDER BY avg_rating DESC LIMIT 10;' },
    { name: '6. Phân tích phân khúc giá Laptop', engine: 'spark', query: "from pyspark.sql import SparkSession\nfrom pyspark.sql.functions import col, when\n\nspark = SparkSession.builder.appName('PriceSegment').getOrCreate()\ndf = spark.read.option('delimiter', '\\t').csv('/user/hadoopthuc/project/input_laptop_products_common')\ndf = df.toDF('brand', 'category', 'date', 'discount', 'discount_rate', 'name', 'original_price', 'price', 'product_id', 'rating', 'sku', 'sold', 'sold_info', 'source', 'url')\n\nsegments = df.withColumn('segment', \n    when(col('price') < 10000000, 'Gia re (<10Tr)')\n    .when((col('price') >= 10000000) & (col('price') <= 20000000), 'Tam trung (10-20Tr)')\n    .otherwise('Cao cap (>20Tr)')\n)\nsegments.groupBy('segment').count().show()\nspark.stop()" },
    { name: '7. Tỷ trọng sản phẩm theo nguồn dữ liệu (Source)', engine: 'hive', query: 'SELECT source, COUNT(*) as product_count FROM laptop_products_common_hive GROUP BY source ORDER BY product_count DESC;' },
    { name: '8. Tổng doanh thu ước tính theo thương hiệu', engine: 'hive', query: 'SELECT brand, sum(price * sold) as total_revenue FROM laptop_products_common_hive WHERE sold > 0 AND price > 0 GROUP BY brand ORDER BY total_revenue DESC LIMIT 10;' },
    { name: '9. Truy vấn bằng Pig: Số lượng Laptop theo hãng', engine: 'pig', query: "data = LOAD '/user/hadoopthuc/project/input_laptop_products_common' USING PigStorage('\\t') AS (brand:chararray, category:chararray, date:chararray, discount:double, discount_rate:double, name:chararray, original_price:double, price:double, product_id:chararray, rating:double, sku:chararray, sold:int, sold_info:chararray, source:chararray, url:chararray);\n\ngrouped = GROUP data BY brand;\ncounts = FOREACH grouped GENERATE group AS brand, COUNT(data) AS total;\nordered = ORDER counts BY total DESC;\ntop10 = LIMIT ordered 10;\nDUMP top10;" }
  ];

  const [query, setQuery] = useState(templates[0].query);
  const [selectedTemplate, setSelectedTemplate] = useState(0);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);

  const handleRunQuery = async () => {
    if (!query.trim()) return alert("Vui lòng nhập câu truy vấn!");
    setLoading(true);
    setResult(null);
    setError(null);
    
    try {
      const response = await fetch('http://localhost:8000/api/run-custom-query/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ engine, query })
      });
      const data = await response.json();
      
      if (data.status === 'success') {
        setResult(data.logs);
      } else {
        setError(data.error_logs || data.message);
      }
    } catch (err) {
      setError("Lỗi kết nối đến máy chủ: " + err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="p-6 w-full h-full flex flex-col animate-fade-in space-y-4">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-white mb-2 font-heading tracking-tight flex items-center gap-3">
            <Terminal size={32} className="text-indigo-400" />
            Interactive Query & Notebook
          </h1>
          <p className="text-slate-400">Chạy truy vấn SQL/Script trực tiếp trên Hadoop Cluster (Hive, Pig, Spark)</p>
        </div>
      </div>

      <div className="bg-slate-800/40 backdrop-blur-md border border-slate-700/50 rounded-2xl shadow-xl overflow-hidden flex flex-col flex-1">
        {/* Toolbar */}
        <div className="bg-slate-800/80 border-b border-slate-700/50 p-4 flex items-center justify-between">
          <div className="flex items-center gap-4">
            <div className="flex items-center gap-2 text-slate-300">
              <Database size={18} className="text-indigo-400"/>
              <span className="font-semibold text-sm">Engine:</span>
              <select 
                value={engine}
                onChange={(e) => {
                  setEngine(e.target.value);
                  if (e.target.value === 'hive') setQuery("CREATE EXTERNAL TABLE IF NOT EXISTS laptop_products_common_hive (\n    brand STRING, category STRING, crawl_date STRING, discount DOUBLE, discount_rate DOUBLE, name STRING, original_price DOUBLE, price DOUBLE, product_id STRING, rating DOUBLE, sku STRING, sold INT, sold_info STRING, source STRING, url STRING\n) ROW FORMAT DELIMITED FIELDS TERMINATED BY '\\t' \nSTORED AS TEXTFILE LOCATION '/user/hadoopthuc/project/input_laptop_products_common';\n\nSELECT brand, COUNT(*) as total FROM laptop_products_common_hive GROUP BY brand ORDER BY total DESC LIMIT 10;");
                  if (e.target.value === 'pig' && query.includes('SELECT')) setQuery("data = LOAD '/user/hadoopthuc/project/input_laptop_products_common' USING PigStorage('\\t') AS (brand:chararray);\nDUMP data;");
                  if (e.target.value === 'spark') setQuery("from pyspark.sql import SparkSession\nspark = SparkSession.builder.appName('Interactive').getOrCreate()\nprint('Spark SQL is ready!')");
                }}
                className="bg-slate-900 border border-slate-600 rounded-lg px-3 py-1.5 text-sm text-white focus:ring-2 focus:ring-indigo-500 outline-none"
              >
                <option value="hive">Apache Hive (SQL)</option>
                <option value="pig">Apache Pig (Pig Latin)</option>
                <option value="spark">Apache Spark (Python/PySpark)</option>
              </select>
            </div>
            
            <div className="w-px h-6 bg-slate-700/50 mx-2"></div>
            
            <div className="flex items-center gap-2 text-slate-300">
              <FileCode size={18} className="text-emerald-400"/>
              <span className="font-semibold text-sm">Mẫu Phân Tích:</span>
              <select 
                value={selectedTemplate}
                onChange={(e) => {
                  const idx = parseInt(e.target.value);
                  setSelectedTemplate(idx);
                  setEngine(templates[idx].engine);
                  setQuery(templates[idx].query);
                }}
                className="bg-slate-900 border border-slate-600 rounded-lg px-3 py-1.5 text-sm text-white focus:ring-2 focus:ring-emerald-500 outline-none max-w-sm truncate"
              >
                {templates.map((tpl, idx) => (
                  <option key={idx} value={idx}>{tpl.name}</option>
                ))}
              </select>
            </div>
          </div>
          
          <button 
            onClick={handleRunQuery}
            disabled={loading}
            className="flex items-center gap-2 bg-indigo-500 hover:bg-indigo-600 disabled:bg-slate-700 disabled:text-slate-500 text-white px-5 py-2 rounded-lg font-medium transition-colors shadow-lg shadow-indigo-500/20"
          >
            {loading ? <RefreshCw size={18} className="animate-spin" /> : <Play size={18} />}
            {loading ? "Đang chạy..." : "Run Query"}
          </button>
        </div>

        <div className="flex flex-1 overflow-hidden">
          {/* Editor Area */}
          <div className="w-1/2 border-r border-slate-700/50 bg-[#1e1e1e] flex flex-col relative group">
            <div className="absolute top-2 right-4 text-xs text-slate-500 font-mono opacity-50 group-hover:opacity-100 transition-opacity">
              <FileCode size={14} className="inline mr-1"/>
              {engine === 'hive' ? 'script.hql' : engine === 'pig' ? 'script.pig' : 'script.py'}
            </div>
            <textarea
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              spellCheck="false"
              className="w-full h-full bg-transparent text-slate-300 p-6 font-mono text-[15px] leading-relaxed resize-none focus:outline-none focus:ring-inset focus:ring-1 focus:ring-indigo-500/30"
              placeholder={`Viết câu lệnh ${engine.toUpperCase()} vào đây...`}
              style={{ tabSize: 4 }}
            />
          </div>

          {/* Results Area */}
          <div className="w-1/2 bg-slate-900 flex flex-col">
            <div className="bg-slate-800/50 px-4 py-2 border-b border-slate-700/50 text-xs font-semibold text-slate-400 uppercase tracking-wider flex justify-between items-center">
              <span>Output / Results</span>
              {result && <span className="text-emerald-400 normal-case flex items-center gap-1"><CheckCircle2 size={14}/> Success</span>}
              {error && <span className="text-rose-400 normal-case flex items-center gap-1"><XCircle size={14}/> Failed</span>}
            </div>
            <div className="p-4 flex-1 overflow-auto custom-scrollbar">
              {loading ? (
                <div className="flex flex-col items-center justify-center h-full text-slate-500 space-y-4">
                  <RefreshCw size={32} className="animate-spin text-indigo-500/50" />
                  <p className="animate-pulse">Đang gửi truy vấn tới Hadoop Cluster...</p>
                </div>
              ) : error ? (
                <pre className="text-rose-400 font-mono text-sm whitespace-pre-wrap">{error}</pre>
              ) : result ? (
                <pre className="text-emerald-400 font-mono text-sm whitespace-pre-wrap">{result}</pre>
              ) : (
                <div className="flex flex-col items-center justify-center h-full text-slate-600">
                  <Terminal size={48} className="mb-4 opacity-20" />
                  <p>Kết quả truy vấn sẽ hiển thị ở đây</p>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default QueryEditor;
