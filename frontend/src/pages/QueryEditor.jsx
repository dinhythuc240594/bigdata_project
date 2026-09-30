import React, { useState, useMemo } from 'react';
import { Play, Database, Terminal, RefreshCw, FileCode, CheckCircle2, XCircle, BarChart3 } from 'lucide-react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Cell } from 'recharts';

const COLORS = ['#6366f1', '#10b981', '#f59e0b', '#ec4899', '#8b5cf6', '#3b82f6'];

const QueryEditor = () => {
  const [engine, setEngine] = useState('hive');
  
  const templates = [
    { name: '1. Khởi tạo bảng Hive (Bắt buộc chạy đầu tiên)', engine: 'hive', query: "CREATE EXTERNAL TABLE IF NOT EXISTS laptop_products_common_hive (\n    brand STRING, category STRING, crawl_date STRING, discount DOUBLE, discount_rate DOUBLE, name STRING, original_price DOUBLE, price DOUBLE, product_id STRING, rating DOUBLE, sku STRING, sold INT, sold_info STRING, source STRING, url STRING\n) ROW FORMAT DELIMITED FIELDS TERMINATED BY '\\t' \nSTORED AS TEXTFILE LOCATION '/user/hadoopthuc/project/input_laptop_products_common';\n\nSHOW TABLES;" },
    { name: '2. Top 10 thương hiệu laptop nhiều sản phẩm nhất', engine: 'hive', query: 'SELECT brand, COUNT(*) as total_products FROM laptop_products_common_hive GROUP BY brand ORDER BY total_products DESC LIMIT 10;' },
    { name: '3. Thống kê giá bán trung bình theo thương hiệu', engine: 'hive', query: 'SELECT brand, ROUND(AVG(price), 0) as avg_price FROM laptop_products_common_hive WHERE price > 0 GROUP BY brand ORDER BY avg_price DESC LIMIT 10;' },
    { name: '4. Top 5 sản phẩm giảm giá sâu nhất', engine: 'hive', query: 'SELECT name, brand, original_price, price, discount_rate FROM laptop_products_common_hive WHERE discount_rate > 0 ORDER BY discount_rate DESC LIMIT 5;' },
    { name: '5. Điểm đánh giá (Rating) trung bình theo hãng', engine: 'hive', query: 'SELECT brand, ROUND(AVG(rating), 2) as avg_rating, sum(sold) as total_sold FROM laptop_products_common_hive WHERE rating > 0 GROUP BY brand ORDER BY avg_rating DESC LIMIT 10;' },
    { name: '6. Phân tích phân khúc giá Laptop', engine: 'spark', query: "from pyspark.sql import SparkSession\nfrom pyspark.sql.functions import col, when\n\nspark = SparkSession.builder.appName('PriceSegment').getOrCreate()\ndf = spark.read.option('delimiter', '\\t').csv('/user/hadoopthuc/project/input_laptop_products_common')\ndf = df.toDF('brand', 'category', 'date', 'discount', 'discount_rate', 'name', 'original_price', 'price', 'product_id', 'rating', 'sku', 'sold', 'sold_info', 'source', 'url')\n\nsegments = df.withColumn('segment', \n    when(col('price') < 10000000, 'Gia re (<10Tr)')\n    .when((col('price') >= 10000000) & (col('price') <= 20000000), 'Tam trung (10-20Tr)')\n    .otherwise('Cao cap (>20Tr)')\n)\nsegments.groupBy('segment').count().show()\nspark.stop()" },
    { name: '7. Tỷ trọng sản phẩm theo nguồn dữ liệu', engine: 'hive', query: 'SELECT source, COUNT(*) as product_count FROM laptop_products_common_hive GROUP BY source ORDER BY product_count DESC;' },
    { name: '8. Tổng doanh thu ước tính theo thương hiệu', engine: 'hive', query: 'SELECT brand, sum(price * sold) as total_revenue FROM laptop_products_common_hive WHERE sold > 0 AND price > 0 GROUP BY brand ORDER BY total_revenue DESC LIMIT 10;' },
    { name: '9. Truy vấn bằng Pig: Số lượng Laptop theo hãng', engine: 'pig', query: "data = LOAD '/user/hadoopthuc/project/input_laptop_products_common' USING PigStorage('\\t') AS (brand:chararray, category:chararray, date:chararray, discount:double, discount_rate:double, name:chararray, original_price:double, price:double, product_id:chararray, rating:double, sku:chararray, sold:int, sold_info:chararray, source:chararray, url:chararray);\n\ngrouped = GROUP data BY brand;\ncounts = FOREACH grouped GENERATE group AS brand, COUNT(data) AS total;\nordered = ORDER counts BY total DESC;\ntop10 = LIMIT ordered 10;\nDUMP top10;" },
    { name: '10. Spark: Top 5 Laptop đắt nhất', engine: 'spark', query: "from pyspark.sql import SparkSession\nfrom pyspark.sql.functions import col\n\nspark = SparkSession.builder.appName('TopExpensive').getOrCreate()\ndf = spark.read.option('delimiter', '\\t').csv('/user/hadoopthuc/project/input_laptop_products_common')\ndf = df.toDF('brand', 'category', 'date', 'discount', 'discount_rate', 'name', 'original_price', 'price', 'product_id', 'rating', 'sku', 'sold', 'sold_info', 'source', 'url')\n\ndf = df.withColumn('price', col('price').cast('double'))\ntop5 = df.filter(col('price') > 0).orderBy(col('price').desc()).select('name', 'price').limit(5)\ntop5.show(truncate=False)\nspark.stop()" },
    { name: '11. Spark: Trung bình giảm giá theo hãng', engine: 'spark', query: "from pyspark.sql import SparkSession\nfrom pyspark.sql.functions import col, avg, round\n\nspark = SparkSession.builder.appName('AvgDiscount').getOrCreate()\ndf = spark.read.option('delimiter', '\\t').csv('/user/hadoopthuc/project/input_laptop_products_common')\ndf = df.toDF('brand', 'category', 'date', 'discount', 'discount_rate', 'name', 'original_price', 'price', 'product_id', 'rating', 'sku', 'sold', 'sold_info', 'source', 'url')\n\ndf = df.withColumn('discount_rate', col('discount_rate').cast('double'))\navg_discount = df.filter(col('discount_rate') > 0).groupBy('brand').agg(round(avg('discount_rate'), 2).alias('avg_discount')).orderBy(col('avg_discount').desc()).limit(10)\navg_discount.show()\nspark.stop()" },
    { name: '12. Spark: Số lượng máy bán ra theo phân khúc', engine: 'spark', query: "from pyspark.sql import SparkSession\nfrom pyspark.sql.functions import col, sum, when\n\nspark = SparkSession.builder.appName('SoldBySegment').getOrCreate()\ndf = spark.read.option('delimiter', '\\t').csv('/user/hadoopthuc/project/input_laptop_products_common')\ndf = df.toDF('brand', 'category', 'date', 'discount', 'discount_rate', 'name', 'original_price', 'price', 'product_id', 'rating', 'sku', 'sold', 'sold_info', 'source', 'url')\n\ndf = df.withColumn('price', col('price').cast('double')).withColumn('sold', col('sold').cast('int'))\nsegments = df.withColumn('segment', \n    when(col('price') < 10000000, 'Gia re (<10Tr)')\n    .when((col('price') >= 10000000) & (col('price') <= 20000000), 'Tam trung (10-20Tr)')\n    .otherwise('Cao cap (>20Tr)')\n)\nresult = segments.groupBy('segment').agg(sum('sold').alias('total_sold')).orderBy(col('total_sold').desc())\nresult.show()\nspark.stop()" }
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
      const response = await fetch(`http://${window.location.hostname}:8000/api/run-custom-query/`, {
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

  const parsedChartData = useMemo(() => {
    if (!result) return null;
    const lines = result.trim().split('\n');
    const data = [];
    
    const isSpark = lines.some(l => l.includes('|'));
    
    for (let line of lines) {
      if (line.includes('INFO') || line.includes('WARN') || line.includes('ERROR') || line.startsWith('+')) continue;
      
      let parts = [];
      if (isSpark && line.includes('|')) {
        parts = line.split('|').map(s => s.trim()).filter(s => s !== '');
      } else {
        parts = line.split('\t');
      }
      
      if (parts.length >= 2) {
        const name = parts[0].trim();
        const val = parseFloat(parts[1].trim());
        if (!isNaN(val) && name !== '' && name !== 'brand' && name !== 'segment' && name !== 'source') {
          data.push({ name: name.substring(0, 20), value: val });
        }
      }
    }
    return data.length > 1 ? data.slice(0, 15) : null;
  }, [result]);

  return (
    <div className="p-6 w-full h-full flex flex-col animate-fade-in space-y-4">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-slate-900 mb-1 font-heading tracking-tight flex items-center gap-3">
            <Terminal size={32} className="text-blue-600" />
            Interactive Query & Notebook
          </h1>
          <p className="text-slate-500">Chạy truy vấn SQL/Script trực tiếp trên Hadoop Cluster</p>
        </div>
      </div>

      <div className="bg-white border border-slate-200 rounded-xl shadow-sm overflow-hidden flex flex-col flex-1">
        {/* Toolbar */}
        <div className="bg-slate-50 border-b border-slate-200 p-4 flex items-center justify-between">
          <div className="flex items-center gap-4">
            <div className="flex items-center gap-2 text-slate-700">
              <Database size={18} className="text-blue-600"/>
              <span className="font-semibold text-sm">Engine:</span>
              <select 
                value={engine}
                onChange={(e) => {
                  const newEngine = e.target.value;
                  setEngine(newEngine);
                  const firstTemplateIdx = templates.findIndex(t => t.engine === newEngine);
                  if (firstTemplateIdx !== -1) {
                    setSelectedTemplate(firstTemplateIdx);
                    setQuery(templates[firstTemplateIdx].query);
                  }
                }}
                className="bg-white border border-slate-300 rounded px-3 py-1.5 text-sm text-slate-800 focus:ring-1 focus:ring-blue-500 outline-none shadow-sm"
              >
                <option value="hive">Apache Hive (SQL)</option>
                <option value="pig">Apache Pig (Pig Latin)</option>
                <option value="spark">Apache Spark (Python/PySpark)</option>
              </select>
            </div>
            
            <div className="w-px h-6 bg-slate-300 mx-2"></div>
            
            <div className="flex items-center gap-2 text-slate-700">
              <FileCode size={18} className="text-emerald-600"/>
              <span className="font-semibold text-sm">Mẫu Phân Tích:</span>
              <select 
                value={selectedTemplate}
                onChange={(e) => {
                  const idx = parseInt(e.target.value);
                  setSelectedTemplate(idx);
                  setEngine(templates[idx].engine);
                  setQuery(templates[idx].query);
                }}
                className="bg-white border border-slate-300 rounded px-3 py-1.5 text-sm text-slate-800 focus:ring-1 focus:ring-blue-500 outline-none max-w-sm truncate shadow-sm"
              >
                {templates.map((tpl, idx) => (
                  tpl.engine === engine ? <option key={idx} value={idx}>{tpl.name}</option> : null
                ))}
              </select>
            </div>
          </div>
          
          <button 
            onClick={handleRunQuery}
            disabled={loading}
            className="flex items-center gap-2 bg-blue-600 hover:bg-blue-700 disabled:bg-slate-300 disabled:text-slate-500 text-white px-5 py-2 rounded font-medium transition-colors shadow-sm"
          >
            {loading ? <RefreshCw size={18} className="animate-spin" /> : <Play size={18} />}
            {loading ? "Đang chạy..." : "Run Query"}
          </button>
        </div>

        <div className="flex flex-col md:flex-row flex-1 overflow-hidden">
          {/* Editor Area */}
          <div className="w-full md:w-1/2 border-r border-slate-200 bg-slate-50 flex flex-col relative group">
            <div className="absolute top-2 right-4 text-xs text-slate-400 font-mono opacity-50 group-hover:opacity-100 transition-opacity">
              <FileCode size={14} className="inline mr-1"/>
              {engine === 'hive' ? 'script.hql' : engine === 'pig' ? 'script.pig' : 'script.py'}
            </div>
            <textarea
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              spellCheck="false"
              className="w-full h-full bg-transparent text-slate-800 p-6 font-mono text-[15px] leading-relaxed resize-none focus:outline-none focus:ring-inset focus:ring-1 focus:ring-blue-500/30"
              placeholder={`Viết câu lệnh ${engine.toUpperCase()} vào đây...`}
              style={{ tabSize: 4 }}
            />
          </div>

          {/* Results Area */}
          <div className="w-full md:w-1/2 bg-white flex flex-col h-full overflow-hidden">
            <div className="bg-slate-50 px-4 py-2 border-b border-slate-200 text-xs font-semibold text-slate-500 uppercase tracking-wider flex justify-between items-center">
              <span>Output / Results</span>
              {result && <span className="text-emerald-600 normal-case flex items-center gap-1"><CheckCircle2 size={14}/> Success</span>}
              {error && <span className="text-red-600 normal-case flex items-center gap-1"><XCircle size={14}/> Failed</span>}
            </div>
            
            <div className="p-4 flex-1 overflow-auto custom-scrollbar flex flex-col space-y-6">
              {loading ? (
                <div className="flex flex-col items-center justify-center h-full text-slate-400 space-y-4">
                  <RefreshCw size={32} className="animate-spin text-blue-500/50" />
                  <p className="animate-pulse">Đang gửi truy vấn tới Hadoop Cluster...</p>
                </div>
              ) : error ? (
                <pre className="text-red-600 font-mono text-sm whitespace-pre-wrap">{error}</pre>
              ) : result ? (
                <>
                  <pre className="text-slate-700 font-mono text-sm whitespace-pre-wrap bg-slate-50 p-4 border border-slate-200 rounded">{result}</pre>
                  
                  {parsedChartData && (
                    <div className="border border-indigo-100 bg-indigo-50/30 rounded-lg p-4 animate-in slide-in-from-bottom-4 fade-in duration-500">
                      <h3 className="font-semibold text-indigo-900 mb-4 flex items-center gap-2">
                        <BarChart3 className="text-indigo-600" size={18} />
                        Auto-generated Chart từ kết quả Hadoop
                      </h3>
                      <div className="h-64 w-full">
                        <ResponsiveContainer width="100%" height="100%">
                          <BarChart data={parsedChartData}>
                            <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#e0e7ff" />
                            <XAxis dataKey="name" stroke="#6366f1" tick={{fontSize: 12}} />
                            <YAxis stroke="#6366f1" tick={{fontSize: 12}} />
                            <Tooltip cursor={{fill: '#e0e7ff', opacity: 0.5}} />
                            <Bar dataKey="value" name="Giá trị" radius={[4, 4, 0, 0]}>
                              {parsedChartData.map((entry, index) => (
                                <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                              ))}
                            </Bar>
                          </BarChart>
                        </ResponsiveContainer>
                      </div>
                    </div>
                  )}
                </>
              ) : (
                <div className="flex flex-col items-center justify-center h-full text-slate-400">
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
