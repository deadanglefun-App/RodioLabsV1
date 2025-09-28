function App() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-900 via-purple-900 to-indigo-900">
      {/* Header */}
      <header className="bg-black/20 backdrop-blur-sm border-b border-white/10">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            <div className="flex items-center space-x-3">
              <div className="w-10 h-10 bg-gradient-to-r from-blue-500 to-purple-600 rounded-lg flex items-center justify-center">
                <span className="text-white font-bold text-xl">R</span>
              </div>
              <div>
                <h1 className="text-white text-xl font-bold">RODIO</h1>
                <p className="text-blue-200 text-xs">Réseau d'Oracles Décentralisés IoT</p>
              </div>
            </div>
            <nav className="hidden md:flex space-x-8">
              <a href="#features" className="text-white/80 hover:text-white transition-colors">Fonctionnalités</a>
              <a href="#architecture" className="text-white/80 hover:text-white transition-colors">Architecture</a>
              <a href="#demo" className="text-white/80 hover:text-white transition-colors">Démo</a>
              <a href="#roadmap" className="text-white/80 hover:text-white transition-colors">Roadmap</a>
            </nav>
          </div>
        </div>
      </header>

      {/* Hero Section */}
      <section className="relative py-20 px-4">
        <div className="max-w-6xl mx-auto text-center">
          <div className="mb-8">
            <span className="inline-block px-4 py-2 bg-blue-500/20 text-blue-200 rounded-full text-sm font-medium mb-6">
              🚀 Le Chainlink de l'IoT sur Polygon
            </span>
          </div>
          
          <h1 className="text-5xl md:text-7xl font-bold text-white mb-6 leading-tight">
            Connectez vos
            <span className="bg-gradient-to-r from-blue-400 to-purple-400 bg-clip-text text-transparent"> capteurs IoT </span>
            à la blockchain
          </h1>
          
          <p className="text-xl text-blue-100 mb-12 max-w-3xl mx-auto leading-relaxed">
            RODIO est un réseau d'oracles décentralisés spécialisé pour l'IoT, offrant des données fiables, 
            sécurisées et vérifiables pour vos smart contracts sur Polygon.
          </p>
          
          <div className="flex flex-col sm:flex-row gap-4 justify-center mb-16">
            <button className="px-8 py-4 bg-gradient-to-r from-blue-600 to-purple-600 text-white rounded-lg font-semibold hover:from-blue-700 hover:to-purple-700 transition-all transform hover:scale-105 shadow-lg">
              Démarrer Maintenant
            </button>
            <button className="px-8 py-4 bg-white/10 text-white rounded-lg font-semibold hover:bg-white/20 transition-all backdrop-blur-sm border border-white/20">
              Voir la Démo
            </button>
          </div>
          
          {/* Stats */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-8 max-w-4xl mx-auto">
            <div className="text-center">
              <div className="text-3xl font-bold text-white mb-2">1000+</div>
              <div className="text-blue-200 text-sm">Capteurs Connectés</div>
            </div>
            <div className="text-center">
              <div className="text-3xl font-bold text-white mb-2">99.9%</div>
              <div className="text-blue-200 text-sm">Uptime</div>
            </div>
            <div className="text-center">
              <div className="text-3xl font-bold text-white mb-2">50ms</div>
              <div className="text-blue-200 text-sm">Latence Moyenne</div>
            </div>
            <div className="text-center">
              <div className="text-3xl font-bold text-white mb-2">$0.001</div>
              <div className="text-blue-200 text-sm">Coût par Transaction</div>
            </div>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section id="features" className="py-20 px-4 bg-black/20">
        <div className="max-w-6xl mx-auto">
          <div className="text-center mb-16">
            <h2 className="text-4xl font-bold text-white mb-4">Pourquoi Choisir RODIO ?</h2>
            <p className="text-xl text-blue-100 max-w-3xl mx-auto">
              Une architecture optimisée pour l'IoT avec des fonctionnalités enterprise
            </p>
          </div>
          
          <div className="grid md:grid-cols-3 gap-8">
            <div className="bg-white/5 backdrop-blur-sm rounded-xl p-8 border border-white/10 hover:bg-white/10 transition-all">
              <div className="w-12 h-12 bg-blue-500/20 rounded-lg flex items-center justify-center mb-6">
                <span className="text-2xl">🔗</span>
              </div>
              <h3 className="text-xl font-bold text-white mb-4">Connectivité Universelle</h3>
              <p className="text-blue-100 mb-4">Support MQTT, HTTP, WebSocket pour tous types de capteurs IoT</p>
              <ul className="text-sm text-blue-200 space-y-2">
                <li>✅ Adaptateurs température, GPS, humidité</li>
                <li>✅ Protocoles légers optimisés</li>
                <li>✅ Formatage automatique blockchain</li>
              </ul>
            </div>
            
            <div className="bg-white/5 backdrop-blur-sm rounded-xl p-8 border border-white/10 hover:bg-white/10 transition-all">
              <div className="w-12 h-12 bg-purple-500/20 rounded-lg flex items-center justify-center mb-6">
                <span className="text-2xl">🛡️</span>
              </div>
              <h3 className="text-xl font-bold text-white mb-4">Sécurité Enterprise</h3>
              <p className="text-blue-100 mb-4">Consensus multi-nœuds avec preuve de stake</p>
              <ul className="text-sm text-blue-200 space-y-2">
                <li>✅ Détection nœuds malhonnêtes</li>
                <li>✅ Système de réputation</li>
                <li>✅ Chiffrement end-to-end</li>
              </ul>
            </div>
            
            <div className="bg-white/5 backdrop-blur-sm rounded-xl p-8 border border-white/10 hover:bg-white/10 transition-all">
              <div className="w-12 h-12 bg-green-500/20 rounded-lg flex items-center justify-center mb-6">
                <span className="text-2xl">📈</span>
              </div>
              <h3 className="text-xl font-bold text-white mb-4">Haute Performance</h3>
              <p className="text-blue-100 mb-4">Architecture asynchrone avec scalabilité automatique</p>
              <ul className="text-sm text-blue-200 space-y-2">
                <li>✅ Latence sub-seconde</li>
                <li>✅ Agrégation intelligente</li>
                <li>✅ Scale horizontal</li>
              </ul>
            </div>
          </div>
        </div>
      </section>

      {/* Architecture Section */}
      <section id="architecture" className="py-20 px-4">
        <div className="max-w-6xl mx-auto">
          <div className="text-center mb-16">
            <h2 className="text-4xl font-bold text-white mb-4">Architecture Chainlink-Style</h2>
            <p className="text-xl text-blue-100 max-w-3xl mx-auto">
              Une architecture modulaire et décentralisée pour une fiabilité maximale
            </p>
          </div>
          
          <div className="bg-white/5 backdrop-blur-sm rounded-xl p-8 border border-white/10">
            <div className="grid md:grid-cols-2 gap-12 items-center">
              <div>
                <h3 className="text-2xl font-bold text-white mb-6">Composants Clés</h3>
                <div className="space-y-4">
                  <div className="flex items-start space-x-4">
                    <div className="w-8 h-8 bg-blue-500/20 rounded-lg flex items-center justify-center flex-shrink-0 mt-1">
                      <span className="text-blue-400 text-sm font-bold">1</span>
                    </div>
                    <div>
                      <h4 className="text-white font-semibold mb-1">Nœuds Gateway</h4>
                      <p className="text-blue-200 text-sm">Collectent les données des capteurs IoT via MQTT/HTTP</p>
                    </div>
                  </div>
                  
                  <div className="flex items-start space-x-4">
                    <div className="w-8 h-8 bg-purple-500/20 rounded-lg flex items-center justify-center flex-shrink-0 mt-1">
                      <span className="text-purple-400 text-sm font-bold">2</span>
                    </div>
                    <div>
                      <h4 className="text-white font-semibold mb-1">Agrégateurs</h4>
                      <p className="text-blue-200 text-sm">Appliquent le consensus et filtrent les outliers</p>
                    </div>
                  </div>
                  
                  <div className="flex items-start space-x-4">
                    <div className="w-8 h-8 bg-green-500/20 rounded-lg flex items-center justify-center flex-shrink-0 mt-1">
                      <span className="text-green-400 text-sm font-bold">3</span>
                    </div>
                    <div>
                      <h4 className="text-white font-semibold mb-1">Validateurs</h4>
                      <p className="text-blue-200 text-sm">Soumettent les données finales sur Polygon</p>
                    </div>
                  </div>
                </div>
              </div>
              
              <div className="bg-black/20 rounded-lg p-6 font-mono text-sm">
                <div className="text-green-400 mb-2"># Architecture RODIO</div>
                <div className="text-blue-300">rodio-node/</div>
                <div className="text-blue-300 ml-2">├── src/</div>
                <div className="text-blue-300 ml-4">│   ├── core/</div>
                <div className="text-white ml-6">│   │   ├── node.py</div>
                <div className="text-white ml-6">│   │   └── aggregator.py</div>
                <div className="text-blue-300 ml-4">│   ├── adapters/</div>
                <div className="text-white ml-6">│   │   ├── temperature.py</div>
                <div className="text-white ml-6">│   │   └── gps.py</div>
                <div className="text-blue-300 ml-4">│   ├── blockchain/</div>
                <div className="text-white ml-6">│   │   └── web3_client.py</div>
                <div className="text-blue-300 ml-4">│   └── security/</div>
                <div className="text-white ml-6">│       └── staking.py</div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Demo Section */}
      <section id="demo" className="py-20 px-4 bg-black/20">
        <div className="max-w-6xl mx-auto">
          <div className="text-center mb-16">
            <h2 className="text-4xl font-bold text-white mb-4">Démo en Temps Réel</h2>
            <p className="text-xl text-blue-100 max-w-3xl mx-auto">
              Observez le consensus multi-nœuds en action
            </p>
          </div>
          
          <div className="grid md:grid-cols-2 gap-8">
            <div className="bg-white/5 backdrop-blur-sm rounded-xl p-6 border border-white/10">
              <h3 className="text-xl font-bold text-white mb-4">📊 Métriques Réseau</h3>
              <div className="space-y-4">
                <div className="flex justify-between items-center">
                  <span className="text-blue-200">Nœuds Actifs</span>
                  <span className="text-white font-bold">3/3</span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-blue-200">Consensus Rate</span>
                  <span className="text-green-400 font-bold">98.5%</span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-blue-200">Latence Moyenne</span>
                  <span className="text-white font-bold">45ms</span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-blue-200">Transactions/h</span>
                  <span className="text-white font-bold">1,247</span>
                </div>
              </div>
            </div>
            
            <div className="bg-white/5 backdrop-blur-sm rounded-xl p-6 border border-white/10">
              <h3 className="text-xl font-bold text-white mb-4">🌡️ Données Capteurs</h3>
              <div className="space-y-4">
                <div className="flex justify-between items-center">
                  <span className="text-blue-200">Température</span>
                  <span className="text-white font-bold">23.5°C</span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-blue-200">Humidité</span>
                  <span className="text-white font-bold">65%</span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-blue-200">GPS</span>
                  <span className="text-white font-bold">48.8566, 2.3522</span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-blue-200">Dernière TX</span>
                  <span className="text-green-400 font-bold">0x1234...abcd</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Roadmap Section */}
      <section id="roadmap" className="py-20 px-4">
        <div className="max-w-6xl mx-auto">
          <div className="text-center mb-16">
            <h2 className="text-4xl font-bold text-white mb-4">Roadmap 2024-2025</h2>
            <p className="text-xl text-blue-100 max-w-3xl mx-auto">
              Notre