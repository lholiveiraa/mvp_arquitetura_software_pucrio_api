import requests  # Importe a biblioteca requests
from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from urllib.parse import quote_plus

from flask_cors import CORS
from flask_cors import cross_origin

from flasgger import Swagger

# from flask_restplus import Api, Resource

# Codificar a senha com urllib.parse.quote_plus
senha = quote_plus('admin@admin')

app = Flask(__name__)

swagger = Swagger(app)

# Configurar o CORS
cors = CORS(app, resources={r"/api/*": {"origins": "*"}})

# Configuração do banco de dados PostgreSQL
app.config['SQLALCHEMY_DATABASE_URI'] = f'postgresql://postgres:{senha}@localhost/pegga'
db = SQLAlchemy(app)

class Carrinho(db.Model):
    __tablename__ = 'carrinho'  # Nome da tabela
    __table_args__ = {'schema': 'ecommerce'}  # Nome do schema

    id = db.Column(db.Integer, primary_key=True)
    cliente_id = db.Column(db.Integer, nullable=False)
    data_compra = db.Column(db.TIMESTAMP, nullable=False)
    status  = db.Column(db.String(10), nullable=False)

    def __init__(self, cliente_id, data_compra, status):
        self.cliente_id = cliente_id
        self.data_compra = data_compra
        self.status = status
        
        
class CarrinhoProdutos(db.Model):
    __tablename__ = 'carrinho_produtos'  # Nome da tabela
    __table_args__ = {'schema': 'ecommerce'}  # Nome do schema

    id = db.Column(db.Integer, primary_key=True)
    carrinho_id = db.Column(db.Integer, nullable=False)
    produto_id = db.Column(db.Integer, nullable=False)
    quantidade  = db.Column(db.Integer, nullable=False)
    preco_unitario  = db.Column(db.Integer, nullable=False)
    preco_unitario = db.Column(db.Numeric(10, 2), nullable=False)
    subtotal = db.Column(db.Numeric(10, 2), nullable=False)
    

    def __init__(self, carrinho_id, produto_id, quantidade, preco_unitario, subtotal):
        self.carrinho_id = carrinho_id
        self.produto_id = produto_id
        self.quantidade = quantidade
        self.preco_unitario = preco_unitario
        self.subtotal = subtotal


# Criar contexto de aplicação
with app.app_context():
    # Cria as tabelas no banco de dados (execute apenas uma vez)
    db.create_all()

# Defina as informações gerais da API
app.config['SWAGGER'] = {
    'title': 'Pegga',
    'version': '1.0',
    'description': 'API para criar carrinhos de compras',
    'basePath': '/api',  # Prefixo para todas as rotas da API
}

# Rota para criar um novo carrinho
@app.route('/carrinho', methods=['POST'])
@cross_origin()
def criar_carrinho():
    """
    Criar um novo carrinho de compras
    ---
    parameters:
      - name: corpo
        in: body
        required: true
        schema:
          type: object
          properties:
            cliente_id:
              type: integer
              description: ID do cliente
            data_compra:
              type: string
              format: date
              description: Data da compra
            status:
              type: string
              description: Status do carrinho
    responses:
      201:
        description: Carrinho criado com sucesso
        schema:
          type: object
          properties:
            message:
              type: string
              description: Mensagem de sucesso
            carrinho_id:
              type: integer
              description: ID do carrinho criado
      400:
        description: Já existe um carrinho para este cliente
    """
    data = request.get_json()
    cliente_id = data.get('cliente_id')

    # Verificar se já existe um carrinho para o cliente_id
    carrinho_existente = Carrinho.query.filter_by(cliente_id=cliente_id).first()

    if carrinho_existente:
        return jsonify({"message": "Um carrinho já existe para este cliente."}), 400

    data_compra = data.get('data_compra')
    status = data.get('status')

    novo_carrinho = Carrinho(cliente_id=cliente_id, data_compra=data_compra, status=status)
    db.session.add(novo_carrinho)
    db.session.commit()

    return jsonify({"message": "Carrinho criado com sucesso!", "carrinho_id": novo_carrinho.id}), 201

# Rota para adicionar um produto ao carrinho
@app.route('/api/carrinho/<int:carrinho_id>/adicionar_produto', methods=['POST'])
@cross_origin()
def adicionar_produto_ao_carrinho(carrinho_id):
    """
    Adicionar um produto ao carrinho de compras
    ---
    parameters:
      - name: carrinho_id
        in: path
        required: true
        type: integer
        description: ID do carrinho de compras
      - name: corpo
        in: body
        required: true
        schema:
          type: object
          properties:
            produto_id:
              type: integer
              description: ID do produto a ser adicionado
            quantidade:
              type: integer
              description: Quantidade do produto a ser adicionada ao carrinho
            preco_unitario:
              type: number
              format: double
              description: Preço unitário do produto
    responses:
      200:
        description: Produto adicionado ao carrinho com sucesso
      404:
        description: Carrinho não encontrado
    """
    carrinho = Carrinho.query.get(carrinho_id)

    if not carrinho:
        return jsonify({"message": "Carrinho não encontrado"}), 404

    data = request.get_json()
    produto_id = data.get('produto_id')
    quantidade = data.get('quantidade')
    preco_unitario = data.get('preco_unitario')
    subtotal = quantidade * preco_unitario

    novo_produto = CarrinhoProdutos(carrinho_id=carrinho_id, produto_id=produto_id, quantidade=quantidade,
                                    preco_unitario=preco_unitario, subtotal=subtotal)
    db.session.add(novo_produto)
    db.session.commit()

    return jsonify({"message": "Produto adicionado ao carrinho com sucesso!"})
# Rota para listar produtos do carrinho
@app.route('/api/carrinho/<int:carrinho_id>/produtos', methods=['GET'])
@cross_origin()
def listar_produtos_do_carrinho(carrinho_id):
    """
    Listar produtos no carrinho de compras
    ---
    parameters:
      - name: carrinho_id
        in: path
        required: true
        type: integer
        description: ID do carrinho de compras
    responses:
      200:
        description: Lista de produtos no carrinho
        schema:
          type: object
          properties:
            produtos:
              type: array
              items:
                type: object
                properties:
                  produto_id:
                    type: integer
                    description: ID do produto
                  quantidade:
                    type: integer
                    description: Quantidade de produtos no carrinho
                  preco_unitario:
                    type: number
                    format: double
                    description: Preço unitário do produto
                  subtotal:
                    type: number
                    format: double
                    description: Subtotal do produto no carrinho
                  detalhes_do_produto:
                    type: object
                    description: Detalhes do produto
      404:
        description: Carrinho não encontrado
    """
    carrinho = Carrinho.query.get(carrinho_id)

    if not carrinho:
        return jsonify({"message": "Carrinho não encontrado"}), 404

    produtos_no_carrinho = CarrinhoProdutos.query.filter_by(carrinho_id=carrinho_id).all()  
    
    produtos_com_detalhes = []
    for produto in produtos_no_carrinho:
        # Fazer uma requisição à outra API para obter os detalhes do produto
        detalhes_do_produto = obter_detalhes_do_produto(produto.produto_id)

        produtos_com_detalhes.append({
            "produto_id": produto.produto_id,
            "quantidade": produto.quantidade,
            "preco_unitario": float(produto.preco_unitario),
            "subtotal": float(produto.subtotal),
            "detalhes_do_produto": detalhes_do_produto  # Adicione os detalhes do produto aqui
        })

    return jsonify({"produtos": produtos_com_detalhes})

# Função para obter os detalhes do produto de outra API
def obter_detalhes_do_produto(produto_id):
    # URL da outra API que fornece os detalhes do produto
    url = f'https://fakestoreapi.com/products/{produto_id}'  # Substitua pela URL real

    try:
        # Fazer uma requisição GET para a outra API
        response = requests.get(url)

        # Verificar se a requisição foi bem-sucedida
        if response.status_code == 200:
            detalhes_do_produto = response.json()
            
            nome_do_produto = detalhes_do_produto.get("title")
            preco_do_produto = detalhes_do_produto.get("price")
            image = detalhes_do_produto.get("image")
            
            return {"nome": nome_do_produto, "preco": preco_do_produto, "image": image }
        else:
            return {"message": "Erro ao obter detalhes do produto da outra API"}, 500
    except Exception as e:
        return {"message": "Erro ao conectar-se à outra API"}, 500
    
    
# Rota para listar carrinho com base no id
@app.route('/api/carrinho/<int:id>', methods=['GET'])
@cross_origin()
def listar_carrinho(id):
    """
    Listar informações do carrinho de compras com base no ID
    ---
    parameters:
      - name: id
        in: path
        required: true
        type: integer
        description: ID do carrinho de compras
    responses:
      200:
        description: Informações do carrinho de compras
        schema:
          type: object
          properties:
            id:
              type: integer
              description: ID do carrinho de compras
            cliente_id:
              type: integer
              description: ID do cliente associado ao carrinho
            data_compra:
              type: string
              format: date-time
              description: Data da compra no formato ISO 8601
            status:
              type: string
              description: Status do carrinho de compras
      404:
        description: Carrinho não encontrado
    """
    carrinho = Carrinho.query.get(id)

    if not carrinho:
        return jsonify({"message": "Carrinho não encontrado"}), 404

    return jsonify({
        "id": carrinho.id,
        "cliente_id": carrinho.cliente_id,
        "data_compra": carrinho.data_compra.isoformat(),  # Converte para string ISO
        "status": carrinho.status
    })

# Rota para remover um produto do carrinho
@app.route('/api/carrinho/<int:carrinho_id>/remover_produto/<int:produto_id>', methods=['DELETE'])
@cross_origin()
def remover_produto_do_carrinho(carrinho_id, produto_id):
    """
    Remover um produto do carrinho de compras
    ---
    parameters:
      - name: carrinho_id
        in: path
        required: true
        type: integer
        description: ID do carrinho de compras
      - name: produto_id
        in: path
        required: true
        type: integer
        description: ID do produto a ser removido do carrinho
    responses:
      200:
        description: Produto removido do carrinho com sucesso
      404:
        description: Carrinho não encontrado ou produto não encontrado no carrinho
    """
    carrinho = Carrinho.query.get(carrinho_id)

    if not carrinho:
        return jsonify({"message": "Carrinho não encontrado"}), 404

    produto = CarrinhoProdutos.query.filter_by(carrinho_id=carrinho_id, produto_id=produto_id).first()

    if not produto:
        return jsonify({"message": "Produto não encontrado no carrinho"}), 404

    db.session.delete(produto)
    db.session.commit()

    return jsonify({"message": "Produto removido do carrinho com sucesso!"})

# Rota para atualizar a quantidade de um produto no carrinho
@app.route('/api/carrinho/<int:carrinho_id>/atualizar_quantidade', methods=['PUT'])
@cross_origin()
def atualizar_quantidade_do_produto_no_carrinho(carrinho_id):
    """
    Atualizar a quantidade de um produto no carrinho de compras
    ---
    parameters:
      - name: carrinho_id
        in: path
        required: true
        type: integer
        description: ID do carrinho de compras
      - name: corpo
        in: body
        required: true
        schema:
          type: object
          properties:
            produto_id:
              type: integer
              description: ID do produto a ser atualizado
            quantidade:
              type: integer
              description: Nova quantidade do produto no carrinho
    responses:
      200:
        description: Quantidade do produto atualizada com sucesso
      404:
        description: Carrinho não encontrado ou produto não encontrado no carrinho
    """
    carrinho = Carrinho.query.get(carrinho_id)

    if not carrinho:
        return jsonify({"message": "Carrinho não encontrado"}), 404

    data = request.get_json()
    produto_id = data.get('produto_id')
    quantidade = data.get('quantidade')

    produto = CarrinhoProdutos.query.filter_by(carrinho_id=carrinho_id, produto_id=produto_id).first()

    if not produto:
        return jsonify({"message": "Produto não encontrado no carrinho"}), 404

    produto.quantidade = quantidade
    produto.subtotal = produto.preco_unitario * quantidade
    db.session.commit()

    return jsonify({"message": "Quantidade do produto atualizada com sucesso!"})


if __name__ == '__main__':
    app.run(debug=True)