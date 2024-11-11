from sqlalchemy import create_engine, Column, Integer, String, Float, Date, Boolean, ForeignKey
from sqlalchemy.orm import relationship, sessionmaker
from datetime import date

# Configuração do banco de dados
engine = create_engine('sqlite:///loja.db', echo=True)
Session = sessionmaker(bind=engine)
session = Session()

# Base declarativa para as classes
from sqlalchemy.ext.declarative import declarative_base
Base = declarative_base()

# Definindo as classes

class Loja(Base):
    __tablename__ = 'lojas'

    id = Column(Integer, primary_key=True)
    nome = Column(String, nullable=False)
    endereco = Column(String, nullable=False)
    
    gerente_id = Column(Integer, ForeignKey('gerentes.id'))
    gerente = relationship("Gerente", back_populates="lojas_gerenciadas")
    funcionarios = relationship("Funcionario", back_populates="loja")
    produtos = relationship("Produto", back_populates="loja")
    pedidos = relationship("Pedido", back_populates="loja")

    def __init__(self, nome, endereco, gerente_id):
        self.nome = nome
        self.endereco = endereco
        self.gerente_id = gerente_id

    @classmethod
    def create(cls, nome, endereco, gerente_id):
        loja = cls(nome, endereco, gerente_id)
        session.add(loja)
        session.commit()
        print(f"Loja '{nome}' criada com sucesso.")
    
    @classmethod
    def read(cls, loja_id):
        loja = session.query(cls).get(loja_id)
        if loja:
            print(f"Loja ID {loja.id} - Nome: {loja.nome}, Endereço: {loja.endereco}")
        else:
            print(f"Loja com ID {loja_id} não encontrada.")
    
    @classmethod
    def update(cls, loja_id, nome=None, endereco=None, gerente_id=None):
        loja = session.query(cls).get(loja_id)
        if loja:
            if nome:
                loja.nome = nome
            if endereco:
                loja.endereco = endereco
            if gerente_id:
                loja.gerente_id = gerente_id
            session.commit()
            print(f"Loja ID {loja.id} atualizada com sucesso.")
        else:
            print(f"Loja com ID {loja_id} não encontrada.")
    
    @classmethod
    def delete(cls, loja_id):
        loja = session.query(cls).get(loja_id)
        if loja:
            session.delete(loja)
            session.commit()
            print(f"Loja ID {loja_id} removida com sucesso.")
        else:
            print(f"Loja com ID {loja_id} não encontrada.")

class Funcionario(Base):
    __tablename__ = 'funcionarios'

    id = Column(Integer, primary_key=True)
    nome = Column(String, nullable=False)
    cargo = Column(String, nullable=False)
    loja_id = Column(Integer, ForeignKey('lojas.id'))
    
    loja = relationship("Loja", back_populates="funcionarios")
    pedidos_processados = relationship("Pedido", back_populates="funcionario")

    def __init__(self, nome, cargo, loja_id):
        self.nome = nome
        self.cargo = cargo
        self.loja_id = loja_id

    @classmethod
    def create(cls, nome, cargo, loja_id):
        funcionario = cls(nome, cargo, loja_id)
        session.add(funcionario)
        session.commit()
        print(f"Funcionário '{nome}' criado com sucesso.")

    @classmethod
    def read(cls, funcionario_id):
        funcionario = session.query(cls).get(funcionario_id)
        if funcionario:
            print(f"Funcionário ID {funcionario.id} - Nome: {funcionario.nome}, Cargo: {funcionario.cargo}")
        else:
            print(f"Funcionário com ID {funcionario_id} não encontrado.")

    @classmethod
    def update(cls, funcionario_id, nome=None, cargo=None, loja_id=None):
        funcionario = session.query(cls).get(funcionario_id)
        if funcionario:
            if nome:
                funcionario.nome = nome
            if cargo:
                funcionario.cargo = cargo
            if loja_id:
                funcionario.loja_id = loja_id
            session.commit()
            print(f"Funcionário ID {funcionario.id} atualizado com sucesso.")
        else:
            print(f"Funcionário com ID {funcionario_id} não encontrado.")
    
    @classmethod
    def delete(cls, funcionario_id):
        funcionario = session.query(cls).get(funcionario_id)
        if funcionario:
            session.delete(funcionario)
            session.commit()
            print(f"Funcionário ID {funcionario_id} removido com sucesso.")
        else:
            print(f"Funcionário com ID {funcionario_id} não encontrado.")

class Pedido(Base):
    __tablename__ = 'pedidos'

    id = Column(Integer, primary_key=True)
    total = Column(Float, nullable=False)
    loja_id = Column(Integer, ForeignKey('lojas.id'))
    funcionario_id = Column(Integer, ForeignKey('funcionarios.id'))

    loja = relationship("Loja", back_populates="pedidos")
    funcionario = relationship("Funcionario", back_populates="pedidos_processados")

    def __init__(self, total, loja_id, funcionario_id):
        self.total = total
        self.loja_id = loja_id
        self.funcionario_id = funcionario_id

    @classmethod
    def create(cls, total, loja_id, funcionario_id):
        pedido = cls(total, loja_id, funcionario_id)
        session.add(pedido)
        session.commit()
        print(f"Pedido de R${total:.2f} criado com sucesso.")
    
    @classmethod
    def read(cls, pedido_id):
        pedido = session.query(cls).get(pedido_id)
        if pedido:
            print(f"Pedido ID {pedido.id} - Total: R${pedido.total:.2f}, Loja ID: {pedido.loja_id}, Funcionário ID: {pedido.funcionario_id}")
        else:
            print(f"Pedido com ID {pedido_id} não encontrado.")

    @classmethod
    def update(cls, pedido_id, total=None, loja_id=None, funcionario_id=None):
        pedido = session.query(cls).get(pedido_id)
        if pedido:
            if total:
                pedido.total = total
            if loja_id:
                pedido.loja_id = loja_id
            if funcionario_id:
                pedido.funcionario_id = funcionario_id
            session.commit()
            print(f"Pedido ID {pedido.id} atualizado com sucesso.")
        else:
            print(f"Pedido com ID {pedido_id} não encontrado.")
    
    @classmethod
    def delete(cls, pedido_id):
        pedido = session.query(cls).get(pedido_id)
        if pedido:
            session.delete(pedido)
            session.commit()
            print(f"Pedido ID {pedido_id} removido com sucesso.")
        else:
            print(f"Pedido com ID {pedido_id} não encontrado.")

class Gerente(Base):
    __tablename__ = 'gerentes'

    id = Column(Integer, primary_key=True)
    nome = Column(String, nullable=False)
    cargo = Column(String, nullable=False)
    
    lojas_gerenciadas = relationship("Loja", back_populates="gerente")

    def __init__(self, nome, cargo):
        self.nome = nome
        self.cargo = cargo

    @classmethod
    def create(cls, nome, cargo):
        gerente = cls(nome, cargo)
        session.add(gerente)
        session.commit()
        print(f"Gerente '{nome}' criado com sucesso.")

    @classmethod
    def read(cls, gerente_id):
        gerente = session.query(cls).get(gerente_id)
        if gerente:
            print(f"Gerente ID {gerente.id} - Nome: {gerente.nome}, Cargo: {gerente.cargo}")
        else:
            print(f"Gerente com ID {gerente_id} não encontrado.")

    @classmethod
    def update(cls, gerente_id, nome=None, cargo=None):
        gerente = session.query(cls).get(gerente_id)
        if gerente:
            if nome:
                gerente.nome = nome
            if cargo:
                gerente.cargo = cargo
            session.commit()
            print(f"Gerente ID {gerente.id} atualizado com sucesso.")
        else:
            print(f"Gerente com ID {gerente_id} não encontrado.")
    
    @classmethod
    def delete(cls, gerente_id):
        gerente = session.query(cls).get(gerente_id)
        if gerente:
            session.delete(gerente)
            session.commit()
            print(f"Gerente ID {gerente_id} removido com sucesso.")
        else:
            print(f"Gerente com ID {gerente_id} não encontrado.")

class Produto(Base):
    __tablename__ = 'produtos'

    id = Column(Integer, primary_key=True)
    nome = Column(String, nullable=False)
    preco = Column(Float, nullable=False)
    estoque = Column(Integer, default=0)
    loja_id = Column(Integer, ForeignKey('lojas.id'))
    loja = relationship("Loja", back_populates="produtos")

    def __init__(self, nome, preco, estoque, loja_id):
        self.nome = nome
        self.preco = preco
        self.estoque = estoque
        self.loja_id = loja_id

    @classmethod
    def create(cls, nome, preco, estoque, loja_id):
        produto = cls(nome, preco, estoque, loja_id)
        session.add(produto)
        session.commit()
        print(f"Produto '{nome}' criado com sucesso.")

    @classmethod
    def read(cls, produto_id):
        produto = session.query(cls).get(produto_id)
        if produto:
            print(f"Produto ID {produto.id} - Nome: {produto.nome}, Preço: R${produto.preco:.2f}, Estoque: {produto.estoque}")
        else:
            print(f"Produto com ID {produto_id} não encontrado.")
    
    @classmethod
    def update(cls, produto_id, nome=None, preco=None, estoque=None, loja_id=None):
        produto = session.query(cls).get(produto_id)
        if produto:
            if nome:
                produto.nome = nome
            if preco:
                produto.preco = preco
            if estoque:
                produto.estoque = estoque
            if loja_id:
                produto.loja_id = loja_id
            session.commit()
            print(f"Produto ID {produto.id} atualizado com sucesso.")
        else:
            print(f"Produto com ID {produto_id} não encontrado.")
    
    @classmethod
    def delete(cls, produto_id):
        produto = session.query(cls).get(produto_id)
        if produto:
            session.delete(produto)
            session.commit()
            print(f"Produto ID {produto_id} removido com sucesso.")
        else:
            print(f"Produto com ID {produto_id} não encontrado.")

# Função para mostrar o menu
def menu():
    while True:
        print("\nMenu:")
        print("1 - Loja")
        print("2 - Funcionário")
        print("3 - Pedido")
        print("4 - Gerente")
        print("5 - Produto")
        print("6 - Sair")
        
        choice = input("Escolha uma opção: ")
        
        if choice == '1':
            crud_menu(Loja)
        elif choice == '2':
            crud_menu(Funcionario)
        elif choice == '3':
            crud_menu(Pedido)
        elif choice == '4':
            crud_menu(Gerente)
        elif choice == '5':
            crud_menu(Produto)
        elif choice == '6':
            print("Saindo...")
            break
        else:
            print("Opção inválida!")

# Função para CRUD de cada classe
def crud_menu(cls):
    while True:
        print(f"\nOperações CRUD para {cls.__name__}:")
        print("1 - Criar")
        print("2 - Ler")
        print("3 - Atualizar")
        print("4 - Deletar")
        print("5 - Voltar")
        
        choice = input("Escolha uma opção: ")
        
        if choice == '1':
            create_item(cls)
        elif choice == '2':
            read_item(cls)
        elif choice == '3':
            update_item(cls)
        elif choice == '4':
            delete_item(cls)
        elif choice == '5':
            break
        else:
            print("Opção inválida!")

def create_item(cls):
    if cls == Loja:
        nome = input("Nome da loja: ")
        endereco = input("Endereço da loja: ")
        gerente_id = int(input("ID do gerente: "))
        cls.create(nome, endereco, gerente_id)
    elif cls == Funcionario:
        nome = input("Nome do funcionário: ")
        cargo = input("Cargo do funcionário: ")
        loja_id = int(input("ID da loja: "))
        cls.create(nome, cargo, loja_id)
    elif cls == Pedido:
        total = float(input("Total do pedido: "))
        loja_id = int(input("ID da loja: "))
        funcionario_id = int(input("ID do funcionário: "))
        cls.create(total, loja_id, funcionario_id)
    elif cls == Gerente:
        nome = input("Nome do gerente: ")
        cargo = input("Cargo do gerente: ")
        cls.create(nome, cargo)
    elif cls == Produto:
        nome = input("Nome do produto: ")
        preco = float(input("Preço do produto: "))
        estoque = int(input("Quantidade em estoque: "))
        loja_id = int(input("ID da loja: "))
        cls.create(nome, preco, estoque, loja_id)

def read_item(cls):
    item_id = int(input("Digite o ID do item: "))
    cls.read(item_id)

def update_item(cls):
    item_id = int(input("Digite o ID do item a ser atualizado: "))
    if cls == Loja:
        nome = input("Novo nome (deixe em branco para não alterar): ")
        endereco = input("Novo endereço (deixe em branco para não alterar): ")
        gerente_id = input("Novo ID do gerente (deixe em branco para não alterar): ")
        cls.update(item_id, nome or None, endereco or None, int(gerente_id) if gerente_id else None)
    elif cls == Funcionario:
        nome = input("Novo nome (deixe em branco para não alterar): ")
        cargo = input("Novo cargo (deixe em branco para não alterar): ")
        loja_id = input("Novo ID da loja (deixe em branco para não alterar): ")
        cls.update(item_id, nome or None, cargo or None, int(loja_id) if loja_id else None)
    elif cls == Pedido:
        total = input("Novo total (deixe em branco para não alterar): ")
        loja_id = input("Novo ID da loja (deixe em branco para não alterar): ")
        funcionario_id = input("Novo ID do funcionário (deixe em branco para não alterar): ")
        cls.update(item_id, float(total) if total else None, int(loja_id) if loja_id else None, int(funcionario_id) if funcionario_id else None)
    elif cls == Gerente:
        nome = input("Novo nome (deixe em branco para não alterar): ")
        cargo = input("Novo cargo (deixe em branco para não alterar): ")
        cls.update(item_id, nome or None, cargo or None)
    elif cls == Produto:
        nome = input("Novo nome (deixe em branco para não alterar): ")
        preco = input("Novo preço (deixe em branco para não alterar): ")
        estoque = input("Novo estoque (deixe em branco para não alterar): ")
        loja_id = input("Novo ID da loja (deixe em branco para não alterar): ")
        cls.update(item_id, nome or None, float(preco) if preco else None, int(estoque) if estoque else None, int(loja_id) if loja_id else None)

def delete_item(cls):
    item_id = int(input("Digite o ID do item a ser removido: "))
    cls.delete(item_id)

# Criar as tabelas no banco de dados
Base.metadata.create_all(engine)

# Iniciar o menu
menu()
