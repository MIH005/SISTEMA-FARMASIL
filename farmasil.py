from sqlalchemy import create_engine, Column, Integer, String, Float, Date, Boolean, ForeignKey, Table
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from datetime import date

# Configuração do banco de dados
engine = create_engine('sqlite:///farmasil.db', echo=True)
Session = sessionmaker(bind=engine)
session = Session()
Base = declarative_base()

# Tabela associativa para o relacionamento muitos-para-muitos entre Gerente e Loja
gerente_loja_associacao = Table(
    'gerente_loja',
    Base.metadata,
    Column('gerente_id', Integer, ForeignKey('gerentes.id'), primary_key=True),
    Column('loja_id', Integer, ForeignKey('lojas.id'), primary_key=True)
)

class Loja(Base):
    __tablename__ = 'lojas'
    id = Column(Integer, primary_key=True)
    nome = Column(String, nullable=False)
    endereco = Column(String, nullable=False)
    horario_funcionamento = Column(String, nullable=False)
    gerentes = relationship('Gerente', secondary=gerente_loja_associacao, back_populates='lojas_gerenciadas')
    produtos = relationship("Produto", back_populates="loja")
    funcionarios = relationship("Funcionario", back_populates="loja")

    def adicionar_loja(self, nome, endereco, horario_funcionamento):
        # Criação de uma instância de Loja com os dados fornecidos
        loja = Loja(nome=nome, endereco=endereco, horario_funcionamento=horario_funcionamento)
        
        # Adiciona a nova loja ao banco de dados
        session.add(loja)
        session.commit()
        
        print("Loja adicionada com sucesso!")

    def atualizar_dados_loja(self, loja_id, nome=None, endereco=None, horario_funcionamento=None):
        loja = session.query(Loja).filter_by(id=loja_id).first()
        if loja:
            if nome:
                loja.nome = nome
            if endereco:
                loja.endereco = endereco
            if horario_funcionamento:
                loja.horario_funcionamento = horario_funcionamento
            session.commit()
            print("Dados da loja atualizados com sucesso!")
        else:
            print("Loja não encontrada.")

    def consultar_dados_loja(self, loja_id):
        loja = session.query(Loja).filter_by(id=loja_id).first()
        if loja:
            print(f"ID: {loja.id}, Nome: {loja.nome}, Endereço: {loja.endereco}, Horário: {loja.horario_funcionamento}")
        else:
            print("Loja não encontrada.")

    def listar_lojas(self):
        lojas = session.query(Loja).all()
        if lojas:
            for loja in lojas:
                print(f"ID: {loja.id}, Nome: {loja.nome}, Endereço: {loja.endereco}, Horário: {loja.horario_funcionamento}")
        else:
            print("Nenhuma loja cadastrada.")

    def consultar_funcionarios_loja(self, loja_id):
        loja = session.query(Loja).filter_by(id=loja_id).first()
        if loja:
            print(f"Funcionários da loja {loja.nome}: {loja.funcionarios if loja.funcionarios else 'Nenhum funcionário cadastrado.'}")
        else:
            print("Loja não encontrada.")

    def adicionar_gerente(self, gerente_id):
        gerente = session.query(Gerente).filter_by(id=gerente_id).first()
        if gerente:
            if gerente not in self.gerentes:
                self.gerentes.append(gerente)
                session.commit()
                print(f"Gerente {gerente.nome} adicionado à loja {self.nome}.")
            else:
                print(f"O gerente {gerente.nome} já está associado à loja {self.nome}.")
        else:
            print("Gerente não encontrado.")

    def verificar_estoque_loja(self, loja_id):
        loja = session.query(Loja).filter_by(id=loja_id).first()
        if loja:
            total_estoque = sum(produto.estoque for produto in loja.produtos)  # Soma do estoque de todos os produtos
            print(f"Estoque total da loja {loja.nome}: {total_estoque if total_estoque > 0 else 'Estoque vazio.'}")
        else:
            print("Loja não encontrada.")

    def remover_loja(self, loja_id):
        loja = session.query(Loja).filter_by(id=loja_id).first()
        if loja:
            session.delete(loja)
            session.commit()
            print("Loja removida com sucesso!")
        else:
            print("Loja não encontrada.")

class Cliente(Base):
    __tablename__ = 'clientes'
    id = Column(Integer, primary_key=True)
    nome = Column(String, nullable=False)
    cpf = Column(String, unique=True, nullable=False)
    telefone = Column(String, nullable=False)
    email = Column(String, nullable=False)
    endereco = Column(String)
    historico_compras = Column(Integer)
    pedidos = relationship('Pedido', back_populates='cliente')  # Adicionando o relacionamento com Pedido

    def __init__(self, nome, cpf, telefone, email, endereco=None):
        self.nome = nome
        self.cpf = cpf
        self.telefone = telefone
        self.email = email
        self.endereco = endereco

    def adicionar_cliente(self, session):
        """Adiciona um cliente ao banco de dados."""
        session.add(self)
        session.commit()
        print(f"Cliente {self.nome} adicionado com sucesso!")

    def remover_cliente(self, session):
        """Remove um cliente do banco de dados."""
        session.delete(self)
        session.commit()
        print(f"Cliente {self.nome} removido com sucesso!")

    def atualizar_dados_cliente(self, nome=None, telefone=None, email=None, endereco=None):
        """Atualiza os dados do cliente."""
        if nome:
            self.nome = nome
        if telefone:
            self.telefone = telefone
        if email:
            self.email = email
        if endereco:
            self.endereco = endereco
        print(f"Dados do cliente {self.nome} atualizados com sucesso!")

class Funcionario(Base):
    __tablename__ = 'funcionarios'
    
    loja = relationship("Loja", back_populates="funcionarios")
    id = Column(Integer, primary_key=True)
    nome = Column(String, nullable=False)
    cargo = Column(String, nullable=False)
    salario = Column(Float, nullable=False)
    turno = Column(String, nullable=False)
    data_admissao = Column(Date, nullable=False, default=date.today)
    loja_id = Column(Integer, ForeignKey('lojas.id'))
    horas_trab = Column(Float, default=0)

    loja = relationship("Loja", back_populates="funcionarios")

    def adicionar_funcionario(self, session):
        """Adiciona o funcionário no banco de dados, verificando se é gerente ou não."""

        # Verificar se o cargo é 'gerente'
        if self.cargo == 'gerente':
            # Verificar se o gerente já está registrado na tabela gerentes
            gerente_existente = session.query(Gerente).filter_by(nome=self.nome).first()

            if not gerente_existente:
                # Se o gerente não existir, adiciona-o à tabela de gerentes
                gerente = Gerente(nome=self.nome, cargo=self.cargo)
                session.add(gerente)
                session.commit()
                print(f"Gerente {self.nome} adicionado à tabela de gerentes.")

            # Após garantir que o gerente está na tabela de gerentes, adiciona o gerente à tabela de funcionários
            funcionario = Funcionario(nome=self.nome, cargo=self.cargo, salario=self.salario, turno=self.turno, loja_id=self.loja_id)
            session.add(funcionario)
            session.commit()
            print(f"Gerente {self.nome} adicionado como funcionário com sucesso!")
        
        else:
            # Se não for gerente, registra como funcionário normal
            session.add(self)
            session.commit()
            print(f"Funcionário {self.nome} adicionado com sucesso!")
        

    def remover_funcionario(self, session):
        """Remove o funcionário do banco de dados."""
        session.delete(self)
        session.commit()
        print(f"Funcionário {self.nome} removido com sucesso.")

    def atualizar_dados(self, session, **kwargs):
        """Atualiza os dados do funcionário."""
        for key, value in kwargs.items():
            setattr(self, key, value)
        session.commit()
        print(f"Dados do funcionário {self.nome} atualizados com sucesso.")

    def registrar_horas(self, horas):
        """Adiciona horas trabalhadas ao funcionário."""
        self.horas_trab += horas
        print(f"{horas} horas registradas para {self.nome}. Total de horas: {self.horas_trab}.") 

    def gerar_relatorio_funcionario(self):
        """Gera um relatório detalhado do funcionário."""
        relatorio = f"""
        Relatório do Funcionário:
        Nome: {self.nome}
        Cargo: {self.cargo}
        Salário: R${self.salario:.2f}
        Turno: {self.turno}
        Data de Admissão: {self.data_admissao}
        Loja ID: {self.loja_id}
        Horas Trabalhadas: {self.horas_trab}
        """
        print(relatorio)
        return relatorio

class Gerente(Base):
    __tablename__ = 'gerentes'

    id = Column(Integer, primary_key=True)
    nome = Column(String, nullable=False)
    cargo = Column(String, nullable=False)

    lojas_gerenciadas = relationship('Loja', secondary=gerente_loja_associacao, back_populates='gerentes')

    def __init__(self, nome, cargo):
        self.nome = nome
        self.cargo = cargo

    def gerenciar_lojas(self, funcionario):
        # Verificar se o funcionário é um gerente
        if funcionario.cargo.lower() != 'gerente':
            print(f"Erro: {funcionario.nome} não tem acesso a este sistema, pois não é gerente.")
            return  # Se não for gerente, interrompe a execução do método

        print(f"Lojas gerenciadas por {self.nome}:")
        for loja in self.lojas_gerenciadas:
            print(f"- {loja.nome} (Endereço: {loja.endereco})")

        escolha = input("Deseja transferir um funcionário ou ajustar o estoque? (transferir/estoque): ").lower()
        if escolha == "transferir":
            nome_funcionario = input("Informe o nome do funcionário a ser transferido: ")
            novo_local = input("Informe o nome da nova loja: ")
            self.transferir_funcionario(nome_funcionario, novo_local)
        elif escolha == "estoque":
            loja_nome = input("Informe o nome da loja: ")
            produto_nome = input("Informe o nome do produto: ")
            quantidade = int(input("Informe a quantidade para ajuste: "))
            self.ajustar_estoque(loja_nome, produto_nome, quantidade)
        else:
            print("Ação inválida.")

    def transferir_funcionario(self, nome_funcionario, nome_nova_loja):
        if not self.verificar_acesso(funcionario):
            return

        funcionario = next((f for f in self.get_funcionarios() if f.nome == nome_funcionario), None)
        nova_loja = next((l for l in self.lojas_gerenciadas if l.nome == nome_nova_loja), None)

        if funcionario and nova_loja:
            funcionario.loja = nova_loja
            session.commit()
            print(f"{funcionario.nome} foi transferido para a loja {nova_loja.nome}.")
        else:
            print("Funcionário ou loja não encontrados.")

    def avaliar_funcionarios(self, funcionario):
        if not self.verificar_acesso(funcionario):
            return

        print(f"Avaliando funcionários das lojas gerenciadas por {self.nome}:")
        for loja in self.lojas_gerenciadas:
            print(f"\nFuncionários na loja {loja.nome}:")
            for funcionario in loja.funcionarios:
                desempenho = len(funcionario.pedidos_processados)  # Assuming pedidos_processados is a list of processed orders
                print(f"- {funcionario.nome}, Cargo: {funcionario.cargo}, Pedidos processados: {desempenho}")
                if desempenho < 5:
                    print(f"⚠ {funcionario.nome} precisa melhorar o desempenho.")
                else:
                    print(f"✔ {funcionario.nome} está com bom desempenho.")

    def ajustar_estoque(self, loja_nome, produto_nome, quantidade, funcionario):
        if not self.verificar_acesso(funcionario):
            return

        loja = next((l for l in self.lojas_gerenciadas if l.nome == loja_nome), None)
        if loja:
            produto = next((p for p in loja.produtos if p.nome == produto_nome), None)
            if produto:
                produto.estoque += quantidade
                session.commit()
                print(f"Estoque de {produto_nome} ajustado para {produto.estoque} unidades.")
            else:
                print(f"Produto {produto_nome} não encontrado na loja {loja_nome}.")
        else:
            print(f"Loja {loja_nome} não encontrada.")

    @staticmethod
    def alterar_preco(produto_id, novo_preco, session):
        """Altera o preço de um produto."""
        produto = session.query(Produto).get(produto_id)
        if produto:
            produto.preco = novo_preco
            session.commit()
            print(f"Preço do produto ID {produto_id} atualizado para R${novo_preco:.2f}.")
        else:
            print(f"Produto ID {produto_id} não encontrado.")

class Pedido(Base):
    __tablename__ = 'pedidos'
    id = Column(Integer, primary_key=True)
    cliente_id = Column(Integer, ForeignKey('clientes.id'))
    funcionario_id = Column(Integer, nullable=False)
    status = Column(String, default="Pendente")
    cliente = relationship('Cliente', back_populates='pedidos')
    itens = relationship("ItensPedido", back_populates="pedido")

    def realizar_pedido(self, cliente_id, funcionario_id, itens):
        cliente = session.query(Cliente).filter_by(id=cliente_id).first()
        if not cliente:
            print("Cliente não encontrado.")
            return

        # Calcular valor total do pedido
        total = 0
        itens_validos = []

        for item in itens:
            nome_produto, quantidade = item['nome'], item['quantidade']
            produto = session.query(Produto).filter_by(nome=nome_produto).first()
            if produto:
                total += produto.preco * quantidade
                itens_validos.append(ItensPedido(produto_id=produto.id, quantidade=quantidade, preco=produto.preco))
            else:
                print(f"Produto '{nome_produto}' não encontrado. O pedido não poderá ser realizado.")

        if not itens_validos:
            print("Nenhum produto válido foi adicionado ao pedido.")
            return

        # Criar pedido
        pedido = Pedido(
            cliente_id=cliente_id,
            funcionario_id=funcionario_id,
            status="Finalizado"
        )
        session.add(pedido)
        session.commit()

        # Adicionar itens ao pedido
        for item in itens_validos:
            item.pedido_id = pedido.id
        session.add_all(itens_validos)
        session.commit()

        print(f"Pedido realizado com sucesso! Total: R${total:.2f}")

        # Gerar nota fiscal
        opcao = input("Deseja gerar nota fiscal? (S/N): ").strip().upper()
        if opcao == 'S':
            self.gerar_nota_fiscal(pedido.id, cliente.nome, total, itens_validos)

    def gerar_nota_fiscal(self, pedido_id, cliente_nome, total, itens):
        nota_fiscal = f"""
        Nota Fiscal - Pedido #{pedido_id}
        Cliente: {cliente_nome}
        Total: R${total:.2f}
        Itens:
        """
        for item in itens:
            produto = session.query(Produto).filter_by(id=item.produto_id).first()
            nota_fiscal += f"{produto.nome} - {item.quantidade} x R${item.preco:.2f}\n"
        
        with open(f"nota_fiscal_pedido_{pedido_id}.txt", "w") as arquivo:
            arquivo.write(nota_fiscal)
        print(f"Nota fiscal gerada: nota_fiscal_pedido_{pedido_id}.txt")

    def consultar_pedidos_cliente(self, cliente_id):
        """Consultar todos os pedidos de um cliente específico."""
        pedidos = session.query(Pedido).filter_by(cliente_id=cliente_id).all()
        if pedidos:
            print(f"Pedidos do cliente com ID {cliente_id}:")
            for pedido in pedidos:
                print(f"- Pedido ID: {pedido.id}, Status: {pedido.status}")
        else:
            print(f"Nenhum pedido encontrado para o cliente com ID {cliente_id}.")

class ItensPedido(Base):
    __tablename__ = 'itens_pedido'
    id = Column(Integer, primary_key=True)
    pedido_id = Column(Integer, ForeignKey('pedidos.id'))
    produto_id = Column(Integer, ForeignKey('produtos.id'))
    quantidade = Column(Integer, nullable=False)
    preco = Column(Float, nullable=False)

    pedido = relationship("Pedido", back_populates="itens")
    produto = relationship("Produto", back_populates="itens_pedido")

class Caixa(Base):
    __tablename__ = 'caixas'
    id = Column(Integer, primary_key=True)
    saldo = Column(Float, default=0.0)  # Saldo inicial do caixa
    registros = relationship("RegistroCaixa", backref="caixa", cascade="all, delete-orphan")

    def registrar_entrada(self, valor):
        if valor <= 0:
            print("Valor de entrada inválido.")
            return
        self.saldo += valor
        registro = RegistroCaixa(tipo="Entrada", valor=valor, caixa_id=self.id)
        session.add(registro)
        session.commit()
        print(f"Entrada de R${valor:.2f} registrada com sucesso.")

    def registrar_saida(self, valor):
        if valor <= 0:
            print("Valor de saída inválido.")
            return
        if self.saldo < valor:
            print("Saldo insuficiente para realizar a saída.")
            return
        self.saldo -= valor
        registro = RegistroCaixa(tipo="Saída", valor=valor, caixa_id=self.id)
        session.add(registro)
        session.commit()
        print(f"Saída de R${valor:.2f} registrada com sucesso.")

    def consultar_saldo(self):
        print(f"Saldo atual do caixa: R${self.saldo:.2f}")

    def fechar_caixa(self):
        print(f"Caixa fechado. Saldo final: R${self.saldo:.2f}")
        self.saldo = 0  # Reseta o saldo após o fechamento
        session.commit()

class RegistroCaixa(Base):
    __tablename__ = 'registros_caixa'
    id = Column(Integer, primary_key=True)
    tipo = Column(String, nullable=False)  # "Entrada" ou "Saída"
    valor = Column(Float, nullable=False)
    caixa_id = Column(Integer, ForeignKey('caixas.id'), nullable=False)
    data_hora = Column(String, default="CURRENT_TIMESTAMP")  # Registrar a data e hora da operação

class Produto(Base):
    __tablename__ = 'produtos'

    id = Column(Integer, primary_key=True)
    nome = Column(String, nullable=False)
    preco = Column(Float, nullable=False)
    categoria = Column(String, nullable=False)
    estoque = Column(Integer, default=0)
    loja_id = Column(Integer, ForeignKey('lojas.id'))  # Relacionamento com Loja
    loja = relationship("Loja", back_populates="produtos")
    itens_pedido = relationship("ItensPedido", back_populates="produto")

    def __init__(self, nome, preco, estoque,categoria, loja_id):
        self.nome = nome
        self.preco = preco
        self.categoria = categoria
        self.estoque = estoque
        self.loja_id = loja_id

    def adicionar_produto(self, session):
        """Adiciona um novo produto ao banco de dados."""
        session.add(self)
        session.commit()
        print(f"Produto {self.nome} adicionado com sucesso!")

    @staticmethod
    def consultar_produto(produto_id, session):
        """Consulta os detalhes de um produto específico."""
        produto = session.query(Produto).get(produto_id)
        if produto:
            print(f"Detalhes do Produto ID {produto_id}:")
            print(f"Nome: {produto.nome}")
            print(f"Preço: R${produto.preco:.2f}")
            print(f"Estoque: {produto.estoque}")
            print(f"Loja ID: {produto.loja_id}")
        else:
            print(f"Produto ID {produto_id} não encontrado.")
            
    @staticmethod
    def buscar_produtos_por_categoria(categoria, session):
        """Busca todos os produtos de uma determinada categoria."""
        produtos = session.query(Produto).filter_by(categoria=categoria).all()
        if produtos:
            print(f"Produtos na categoria {categoria}:")
            for produto in produtos:
                print(f"- Produto ID {produto.id}: {produto.nome}, R${produto.preco:.2f}, Estoque: {produto.estoque}")
        else:
            print(f"Nenhum produto encontrado na categoria {categoria}.")

    @staticmethod
    def verificar_estoque(produto_id, quantidade, session):
        """Verifica se o estoque de um produto é suficiente."""
        produto = session.query(Produto).get(produto_id)
        if produto:
            if produto.estoque >= quantidade:
                print(f"Estoque suficiente para o produto ID {produto_id}.")
                return True
            else:
                print(f"Estoque insuficiente para o produto ID {produto_id}. Disponível: {produto.estoque}.")
                return False
        else:
            print(f"Produto ID {produto_id} não encontrado.")
            return False

    @staticmethod
    def listar_produtos_loja(loja_id, session):
        """Lista todos os produtos disponíveis em uma loja específica."""
        produtos = session.query(Produto).filter_by(loja_id=loja_id).all()
        if produtos:
            print(f"Produtos na Loja ID {loja_id}:")
            for produto in produtos:
                print(f"- Produto ID {produto.id}: {produto.nome}, R${produto.preco:.2f}, Estoque: {produto.estoque}")
        else:
            print(f"Nenhum produto encontrado na Loja ID {loja_id}.")

Base.metadata.create_all(engine)

def menu_principal():
    while True:
        print("\n--- Sistema Farmasil ---")
        print("1. Gerenciar Lojas")
        print("2. Gerenciar Clientes")
        print("3. Gerenciar Funcionários")
        print("4. Gerenciar Gerentes")
        print("5. Gerenciar Pedidos")
        print("6. Gerenciar Caixa")
        print("7. Gerenciar Produtos")
        print("0. Sair")
        
        opcao = input("Escolha uma opção: ")
        
        if opcao == "1":
            menu_loja()
        elif opcao == "2":
            menu_cliente()
        elif opcao == "3":
            menu_funcionario()
        elif opcao == "4":
            menu_gerente()
        elif opcao == "5":
            menu_pedidos()
        elif opcao == "6":
            menu_caixa()
        elif opcao == "7":
            menu_produtos()
        elif opcao == "0":
            print("Saindo do sistema...")
            break
        else:
            print("Opção inválida. Tente novamente.")

# Funções de menu para cada categoria
def menu_loja():
    while True:
        print("\n--- Gerenciamento de Lojas ---")
        print("1. Adicionar Loja")
        print("2. Atualizar Dados da Loja")
        print("3. Consultar Dados da Loja")
        print("4. Listar Todas as Lojas")
        print("5. Consultar Funcionários da Loja")
        print("6. Verificar Estoque da Loja")
        print("7. Remover Loja")
        print("8. Adicionar Gerente a Loja")
        print("0. Voltar")
        
        opcao = input("Escolha uma opção: ")
        
        if opcao == "1":
            nome = input("Nome da loja: ")
            endereco = input("Endereço da loja: ")
            horario_funcionamento = input("Horário de funcionamento: ")
            Loja().adicionar_loja(nome, endereco, horario_funcionamento)
        
        elif opcao == "2":
            loja_id = int(input("ID da loja a ser atualizada: "))
            nome = input("Novo nome (ou Enter para manter): ")
            endereco = input("Novo endereço (ou Enter para manter): ")
            horario_funcionamento = input("Novo horário (ou Enter para manter): ")
            Loja().atualizar_dados_loja(loja_id, nome, endereco, horario_funcionamento)
        
        elif opcao == "3":
            loja_id = int(input("ID da loja: "))
            Loja().consultar_dados_loja(loja_id)
        
        elif opcao == "4":
            Loja().listar_lojas()
        
        elif opcao == "5":
            loja_id = int(input("ID da loja: "))
            Loja().consultar_funcionarios_loja(loja_id)
        
        elif opcao == "6":
            loja_id = int(input("ID da loja: "))
            Loja().verificar_estoque_loja(loja_id)
        
        elif opcao == "7":
            loja_id = int(input("ID da loja a ser removida: "))
            Loja().remover_loja(loja_id)
        
        elif opcao == "8":
            loja_id = int(input("ID da loja: "))
            loja = session.query(Loja).filter_by(id=loja_id).first()
            if loja:
                gerente_id = int(input("ID do gerente a ser adicionado: "))
                loja.adicionar_gerente(gerente_id)
            else:
                print("Loja não encontrada.")
        
        elif opcao == "0":
            break
        
        else:
            print("Opção inválida. Tente novamente.")

def menu_caixa():
    # Verifica se o caixa já existe no banco
    caixa = session.query(Caixa).first()
    if not caixa:
        # Se não existir, cria um novo e adiciona à sessão
        caixa = Caixa(saldo=0.0)
        session.add(caixa)
        session.commit()

    while True:
        print("\n--- Gerenciamento de Caixa ---")
        print("1. Registrar Entrada")
        print("2. Registrar Saída")
        print("3. Consultar Saldo")
        print("4. Fechar Caixa")
        print("0. Voltar")
        opcao = input("Escolha uma opção: ")

        if opcao == "1":
            try:
                valor = float(input("Informe o valor da entrada: R$ "))
                caixa.registrar_entrada(valor)
            except ValueError:
                print("Valor inválido. Tente novamente.")

        elif opcao == "2":
            try:
                valor = float(input("Informe o valor da saída: R$ "))
                caixa.registrar_saida(valor)
            except ValueError:
                print("Valor inválido. Tente novamente.")

        elif opcao == "3":
            caixa.consultar_saldo()

        elif opcao == "4":
            caixa.fechar_caixa()
            break

        elif opcao == "0":
            break

        else:
            print("Opção inválida. Tente novamente.")

def menu_cliente():
    while True:
        print("\n--- Gerenciamento de Clientes ---")
        print("1. Adicionar Cliente")
        print("2. Atualizar Dados do Cliente")
        print("3. Consultar Dados do Cliente")
        print("4. Listar Todos os Clientes")
        print("5. Remover Cliente")
        print("0. Voltar")
        
        opcao = input("Escolha uma opção: ")
        
        if opcao == "1":
            nome = input("Nome do cliente: ")
            cpf = input("CPF do cliente: ")
            telefone = input("Telefone do cliente: ")
            email = input("Email do cliente: ")
            endereco = input("Endereço do cliente (opcional): ")
            cliente = Cliente(nome, cpf, telefone, email, endereco)
            cliente.adicionar_cliente(session)
        
        elif opcao == "2":
            cliente_id = int(input("ID do cliente a ser atualizado: "))
            cliente = session.query(Cliente).filter_by(id=cliente_id).first()
            if cliente:
                nome = input("Novo nome (ou Enter para manter): ")
                telefone = input("Novo telefone (ou Enter para manter): ")
                email = input("Novo email (ou Enter para manter): ")
                endereco = input("Novo endereço (ou Enter para manter): ")
                cliente.atualizar_dados_cliente(nome, telefone, email, endereco)
                session.commit()
                print("Dados do cliente atualizados com sucesso!")
            else:
                print("Cliente não encontrado.")
        
        elif opcao == "3":
            cliente_id = int(input("ID do cliente: "))
            cliente = session.query(Cliente).filter_by(id=cliente_id).first()
            if cliente:
                print(f"ID: {cliente.id}, Nome: {cliente.nome}, CPF: {cliente.cpf}, "
                      f"Telefone: {cliente.telefone}, Email: {cliente.email}, "
                      f"Endereço: {cliente.endereco}, Histórico de Compras: {cliente.historico_compras}")
            else:
                print("Cliente não encontrado.")
        
        elif opcao == "4":
            clientes = session.query(Cliente).all()
            if clientes:
                for cliente in clientes:
                    print(f"ID: {cliente.id}, Nome: {cliente.nome}, CPF: {cliente.cpf}, "
                          f"Telefone: {cliente.telefone}, Email: {cliente.email}, "
                          f"Nível de Fidelidade: {cliente.nivel_fidelidade}")
            else:
                print("Nenhum cliente cadastrado.")
        
        elif opcao == "5":
            cliente_id = int(input("ID do cliente a ser removido: "))
            cliente = session.query(Cliente).filter_by(id=cliente_id).first()
            if cliente:
                cliente.remover_cliente(session)
            else:
                print("Cliente não encontrado.")
        
        elif opcao == "0":
            break
        
        else:
            print("Opção inválida. Tente novamente.")

def menu_funcionario():
    while True:
        print("\n--- Gerenciamento de Funcionários ---")
        print("1. Adicionar Funcionário")
        print("2. Atualizar Dados do Funcionário")
        print("3. Consultar Dados do Funcionário")
        print("4. Listar Todos os Funcionários")
        print("5. Registrar Horas Trabalhadas")
        print("6. Gerar Relatório do Funcionário")
        print("7. Remover Funcionário")
        print("0. Voltar")
        
        opcao = input("Escolha uma opção: ")
        
        if opcao == "1":
            nome = input("Nome do funcionário: ")
            cargo = input("Cargo do funcionário: ")
            salario = float(input("Salário do funcionário: "))
            turno = input("Turno do funcionário: ")
            loja_id = int(input("ID da loja onde o funcionário trabalha: "))
            funcionario = Funcionario(nome=nome, cargo=cargo, salario=salario, turno=turno, loja_id=loja_id)
            funcionario.adicionar_funcionario(session)
        
        elif opcao == "2":
            funcionario_id = int(input("ID do funcionário a ser atualizado: "))
            funcionario = session.query(Funcionario).filter_by(id=funcionario_id).first()
            if funcionario:
                nome = input("Novo nome (ou Enter para manter): ")
                cargo = input("Novo cargo (ou Enter para manter): ")
                salario = input("Novo salário (ou Enter para manter): ")
                turno = input("Novo turno (ou Enter para manter): ")
                kwargs = {}
                if nome: kwargs['nome'] = nome
                if cargo: kwargs['cargo'] = cargo
                if salario: kwargs['salario'] = float(salario)
                if turno: kwargs['turno'] = turno
                funcionario.atualizar_dados(session, **kwargs)
            else:
                print("Funcionário não encontrado.")
        
        elif opcao == "3":
            funcionario_id = int(input("ID do funcionário: "))
            funcionario = session.query(Funcionario).filter_by(id=funcionario_id).first()
            if funcionario:
                print(f"ID: {funcionario.id}, Nome: {funcionario.nome}, Cargo: {funcionario.cargo}, "
                      f"Salário: R${funcionario.salario:.2f}, Turno: {funcionario.turno}, "
                      f"Data de Admissão: {funcionario.data_admissao}, Loja ID: {funcionario.loja_id}, "
                      f"Horas Trabalhadas: {funcionario.horas_trab}")
            else:
                print("Funcionário não encontrado.")
        
        elif opcao == "4":
            funcionarios = session.query(Funcionario).all()
            if funcionarios:
                for funcionario in funcionarios:
                    print(f"ID: {funcionario.id}, Nome: {funcionario.nome}, Cargo: {funcionario.cargo}, "
                          f"Salário: R${funcionario.salario:.2f}, Turno: {funcionario.turno}, "
                          f"Data de Admissão: {funcionario.data_admissao}, Horas Trabalhadas: {funcionario.horas_trab}")
            else:
                print("Nenhum funcionário cadastrado.")
        
        elif opcao == "5":
            funcionario_id = int(input("ID do funcionário: "))
            funcionario = session.query(Funcionario).filter_by(id=funcionario_id).first()
            if funcionario:
                horas = float(input("Quantidade de horas trabalhadas: "))
                funcionario.registrar_horas(horas)
                session.commit()
            else:
                print("Funcionário não encontrado.")
        
        elif opcao == "6":
            funcionario_id = int(input("ID do funcionário: "))
            funcionario = session.query(Funcionario).filter_by(id=funcionario_id).first()
            if funcionario:
                funcionario.gerar_relatorio_funcionario()
            else:
                print("Funcionário não encontrado.")
        
        elif opcao == "7":
            funcionario_id = int(input("ID do funcionário a ser removido: "))
            funcionario = session.query(Funcionario).filter_by(id=funcionario_id).first()
            if funcionario:
                funcionario.remover_funcionario(session)
            else:
                print("Funcionário não encontrado.")
        
        elif opcao == "0":
            break
        
        else:
            print("Opção inválida. Tente novamente.")


def menu_gerente():
    while True:
        print("\n--- Gerenciamento de Gerentes ---")
        print("1. Ver Lojas Gerenciadas")
        print("2. Transferir Funcionário")
        print("3. Ajustar Estoque de um Produto")
        print("4. Avaliar Funcionários")
        print("5. Alterar Preço de um Produto")
        print("0. Voltar")
        
        opcao = input("Escolha uma opção: ")
        
        # Obter o ID do funcionário atual
        funcionario_id = int(input("Informe o ID do seu usuário (funcionário): "))
        funcionario_atual = session.query(Funcionario).filter_by(id=funcionario_id).first()

        # Verificar se o funcionário é gerente
        if not funcionario_atual or funcionario_atual.cargo.lower() != 'gerente':
            print(f"Erro: {funcionario_atual.nome if funcionario_atual else 'Funcionário'} não tem acesso a este sistema, pois não é gerente.")
            continue  # Se não for gerente, volta ao menu
        
        # A partir daqui, o funcionário é um gerente, e o código pode continuar
        if opcao == "1":
            gerente_id = int(input("ID do gerente: "))
            gerente = session.query(Gerente).filter_by(id=gerente_id).first()
            if gerente:
                gerente.gerenciar_lojas(funcionario_atual)
            else:
                print("Gerente não encontrado.")
        
        elif opcao == "2":
            gerente_id = int(input("ID do gerente: "))
            gerente = session.query(Gerente).filter_by(id=gerente_id).first()
            if gerente:
                nome_funcionario = input("Nome do funcionário a ser transferido: ")
                nova_loja = input("Nome da nova loja: ")
                gerente.transferir_funcionario(nome_funcionario, nova_loja, funcionario_atual)
            else:
                print("Gerente não encontrado.")
        
        elif opcao == "3":
            gerente_id = int(input("ID do gerente: "))
            gerente = session.query(Gerente).filter_by(id=gerente_id).first()
            if gerente:
                loja_nome = input("Nome da loja: ")
                produto_nome = input("Nome do produto: ")
                quantidade = int(input("Quantidade para ajuste: "))
                gerente.ajustar_estoque(loja_nome, produto_nome, quantidade, funcionario_atual)
            else:
                print("Gerente não encontrado.")
        
        elif opcao == "4":
            gerente_id = int(input("ID do gerente: "))
            gerente = session.query(Gerente).filter_by(id=gerente_id).first()
            if gerente:
                gerente.avaliar_funcionarios(funcionario_atual)
            else:
                print("Gerente não encontrado.")
        
        elif opcao == "5":
            # Alterar preço de um produto (somente se o funcionário for gerente)
            gerente_id = int(input("ID do gerente: "))
            gerente = session.query(Gerente).filter_by(id=gerente_id).first()
            if gerente:
                produto_id = int(input("ID do produto a ter o preço alterado: "))
                novo_preco = float(input("Novo preço do produto: R$ "))
                Gerente.alterar_preco(produto_id, novo_preco, session)
            else:
                print("Gerente não encontrado.")
        
        elif opcao == "0":
            break
        
        else:
            print("Opção inválida. Tente novamente.")
    return

def menu_pedidos():
    while True:
        print("\n--- Gerenciamento de Pedidos ---")
        print("1. Realizar Pedido")
        print("2. Remover Item de Pedido")
        print("3. Consultar Pedidos de um Cliente")
        print("0. Voltar")
        
        opcao = input("Escolha uma opção: ")
        
        if opcao == "1":
            cliente_id = int(input("ID do Cliente: "))
            funcionario_id = int(input("ID do Funcionário: "))
            
            itens = []
            while True:
                nome_produto = input("Digite o nome do produto (ou 'fim' para finalizar): ")
                if nome_produto.lower() == 'fim':
                    break

                # Verificar se o produto existe no banco
                produto = session.query(Produto).filter_by(nome=nome_produto).first()
                if not produto:
                    print(f"Produto '{nome_produto}' não encontrado. Tente novamente.")
                    continue
                
                quantidade = int(input(f"Digite a quantidade de '{nome_produto}': "))
                itens.append({'nome': nome_produto, 'quantidade': quantidade})

            if itens:
                pedido = Pedido()
                pedido.realizar_pedido(cliente_id, funcionario_id, itens)
            else:
                print("Nenhum item foi adicionado ao pedido.")

        elif opcao == "2":
            pedido_id = int(input("ID do Pedido: "))
            item_nome = input("Nome do item a ser removido: ")
            pedido = session.query(Pedido).filter_by(id=pedido_id).first()
            if pedido:
                pedido.remover_item_pedido(pedido_id, item_nome)
            else:
                print("Pedido não encontrado.")
        
        elif opcao == "3":
            cliente_id = int(input("ID do Cliente: "))
            pedido = Pedido()  # Criar uma instância de Pedido para chamar o método
            pedido.consultar_pedidos_cliente(cliente_id)
        
        elif opcao == "0":
            break  # Volta ao menu principal
        
        else:
            print("Opção inválida. Tente novamente.")

def menu_produtos():
    while True:
        print("\n--- Gerenciamento de Produtos ---")
        print("1. Adicionar Produto")
        print("2. Remover Produto")
        print("3. Consultar Produto")
        print("4. Buscar Produtos por Categoria")
        print("5. Verificar Estoque de Produto")
        print("6. Listar Produtos de uma Loja")
        print("0. Voltar")
        
        opcao = input("Escolha uma opção: ")
        
        if opcao == "1":
            nome = input("Digite o nome do produto: ")
            preco = float(input("Digite o preço do produto: "))
            estoque = int(input("Digite a quantidade em estoque: "))
            categoria = input("Digite a categoria do produto: ")
            loja_id = int(input("Digite o ID da loja: "))
            novo_produto = Produto(nome, preco, estoque, categoria,loja_id)
            novo_produto.adicionar_produto(session)
        
        elif opcao == "2":
            produto_id = int(input("Digite o ID do produto para remover: "))
            Produto.remover_produto(produto_id, session)
        
        elif opcao == "3":
            produto_id = int(input("Digite o ID do produto para consultar: "))
            Produto.consultar_produto(produto_id, session)
        
        elif opcao == "4":
            categoria = input("Digite a categoria dos produtos a serem buscados: ")
            Produto.buscar_produtos_por_categoria(categoria, session)
        
        elif opcao == "5":
            produto_id = int(input("Digite o ID do produto para verificar o estoque: "))
            quantidade = int(input("Digite a quantidade a ser verificada: "))
            Produto.verificar_estoque(produto_id, quantidade, session)
        
        elif opcao == "6":
            loja_id = int(input("Digite o ID da loja para listar os produtos: "))
            Produto.listar_produtos_loja(loja_id, session)
        
        elif opcao == "0":
            break  # Volta ao menu principal
        
        else:
            print("Opção inválida. Tente novamente.")
menu_principal()
