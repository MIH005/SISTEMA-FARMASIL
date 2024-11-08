from sqlalchemy import create_engine, Column, Integer, String, Float, Date, ForeignKey, Boolean
from sqlalchemy.orm import relationship, sessionmaker
from datetime import date, datetime
import os, sys
from sqlalchemy.orm import declarative_base
Base = declarative_base()

class Loja(Base):
    __tablename__ = 'lojas'

    id = Column(Integer, primary_key=True)
    gerente_id = Column(Integer, ForeignKey('gerentes.id'))
    gerente = relationship("Gerente", back_populates="lojas_gerenciadas")
    pedidos = relationship("Pedido", back_populates="loja")
    funcionarios = relationship("Funcionario", back_populates="loja")
    produtos = relationship("Produto", back_populates="loja")  # Relacionamento com Produto

    endereco = Column(String, nullable=False)
    telefone = Column(Integer, nullable=False)
    hora_funcionamento = Column(String, nullable=False)

    def __init__(self, endereco, telefone, hora_funcionamento):
        self.endereco = endereco
        self.telefone = telefone
        self.hora_funcionamento = hora_funcionamento

    def adicionar_loja(self, session):
        """Adiciona uma nova loja ao sistema."""
        session.add(self)
        session.commit()
        print(f"Loja adicionada: {self.endereco}, {self.telefone}, {self.hora_funcionamento}")

    def remover_loja(self, session):
        """Remove uma loja do sistema."""
        session.delete(self)
        session.commit()
        print(f"Loja removida: {self.endereco}")

    def atualizar_dados(self, session, endereco=None, telefone=None, hora_funcionamento=None):
        """Atualiza os dados de uma loja."""
        if endereco:
            self.endereco = endereco
        if telefone:
            self.telefone = telefone
        if hora_funcionamento:
            self.hora_funcionamento = hora_funcionamento
        session.commit()
        print(f"Dados da loja {self.id} atualizados.")

    def consultar_dados(self):
        """Consulta os dados de uma loja."""
        print(f"Dados da loja {self.id}:")
        print(f"- Endereço: {self.endereco}")
        print(f"- Telefone: {self.telefone}")
        print(f"- Horário de Funcionamento: {self.hora_funcionamento}")

    @staticmethod
    def listar_dados(session):
        """Lista todas as lojas cadastradas no sistema."""
        lojas = session.query(Loja).all()
        if lojas:
            for loja in lojas:
                loja.consultar_dados()
        else:
            print("Nenhuma loja cadastrada.")

    def consultar_funcionarios_loja(self, session):
        """Consulta os funcionários de uma loja."""
        funcionarios = session.query(Funcionario).filter_by(loja_id=self.id).all()
        if funcionarios:
            print(f"Funcionários da loja {self.id}:")
            for funcionario in funcionarios:
                print(f"- {funcionario.nome} ({funcionario.cargo})")
        else:
            print(f"Não há funcionários cadastrados na loja {self.id}.")

    def verificar_estoque_loja(self, session):
        """Verifica o estoque total de produtos de uma loja."""
        produtos = session.query(Produto).filter_by(loja_id=self.id).all()
        if produtos:
            print(f"Estoque da loja {self.id}:")
            for produto in produtos:
                print(f"- {produto.categoria}: {produto.estoque} unidades")
        else:
            print(f"A loja {self.id} não tem produtos cadastrados.")

    def ajustar_estoque(self, session, produto_id, quantidade):
        """Ajusta o estoque de um produto específico."""
        produto = session.query(Produto).filter_by(id=produto_id, loja_id=self.id).first()
        if produto:
            produto.ajustar_estoque(quantidade, session)
        else:
            print("Produto não encontrado na loja.")

    def alterar_hora_funcionamento(self, novo_horario, session):
        """Altera os horários de funcionamento de uma loja."""
        self.hora_funcionamento = novo_horario
        session.commit()
        print(f"Horário de funcionamento da loja {self.id} alterado para {self.hora_funcionamento}.")


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

    def adicionar_funcionario(self, session):
        """Adiciona o funcionário no banco de dados."""
        session.add(self)
        session.commit()
        print(f"Funcionário {self.nome} adicionado com sucesso.")

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

    def calcular_pagamento(self):
        """Calcula o pagamento com base no salário e horas extras."""
        valor_hora = self.salario / 160  # Base de 160 horas mensais
        pagamento = self.salario
        if self.horas_trab > 160:
            horas_extras = self.horas_trab - 160
            pagamento += horas_extras * valor_hora * 1.5  # 50% a mais por hora extra
        print(f"Pagamento para {self.nome}: R${pagamento:.2f}")
        return pagamento

    def listar_funcionarios(session, loja_id):
        """Lista todos os funcionários de uma loja."""
        funcionarios = session.query(Funcionario).filter_by(loja_id=loja_id).all()
        if funcionarios:
            print(f"Funcionários da loja {loja_id}:")
            for func in funcionarios:
                print(f"- {func.nome} ({func.cargo})")
        else:
            print(f"Nenhum funcionário encontrado para a loja {loja_id}.")

    def registrar_horas(self, horas):
        """Adiciona horas trabalhadas ao funcionário."""
        self.horas_trab += horas
        print(f"{horas} horas registradas para {self.nome}. Total de horas: {self.horas_trab}.")

    def promover(self, novo_cargo, novo_salario):
        """Promove o funcionário a um novo cargo e ajusta seu salário."""
        self.cargo = novo_cargo
        self.salario = novo_salario
        print(f"{self.nome} foi promovido para {self.cargo} com salário de R${self.salario:.2f}.")

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
    
    lojas_gerenciadas = relationship("Loja", back_populates="gerente")

    def __init__(self, nome, cargo):
        self.nome = nome
        self.cargo = cargo

    def gerenciar_lojas(self):
        print(f"Lojas gerenciadas por {self.nome}:")
        for loja in self.lojas_gerenciadas:
            print(f"- {loja.nome} (Endereço: {loja.endereco})")
        
        # Exemplos de ações de gerenciamento
        escolha = input("Deseja transferir um funcionário ou ajustar o estoque? (transferir/estoque): ").lower()
        if escolha == "transferir":
            # Implementar transferência de funcionário
            nome_funcionario = input("Informe o nome do funcionário a ser transferido: ")
            novo_local = input("Informe o nome da nova loja: ")
            self.transferir_funcionario(nome_funcionario, novo_local)
        elif escolha == "estoque":
            # Ajustar estoque de uma loja
            loja_nome = input("Informe o nome da loja: ")
            produto_nome = input("Informe o nome do produto: ")
            quantidade = int(input("Informe a quantidade para ajuste: "))
            self.ajustar_estoque(loja_nome, produto_nome, quantidade)
        else:
            print("Ação inválida.")

    def transferir_funcionario(self, nome_funcionario, nome_nova_loja):
        # Lógica para transferir um funcionário entre lojas
        funcionario = next((f for f in self.get_funcionarios() if f.nome == nome_funcionario), None)
        nova_loja = next((l for l in self.lojas_gerenciadas if l.nome == nome_nova_loja), None)

        if funcionario and nova_loja:
            funcionario.loja = nova_loja
            session.commit()
            print(f"{funcionario.nome} foi transferido para a loja {nova_loja.nome}.")
        else:
            print("Funcionário ou loja não encontrados.")

    def monitorar_vendas(self):
        print(f"Relatório de vendas das lojas gerenciadas por {self.nome}:")
        for loja in self.lojas_gerenciadas:
            total_vendas = sum(pedido.total for pedido in loja.pedidos)
            print(f"- Loja: {loja.nome}, Total de vendas: R${total_vendas:.2f}")

    def avaliar_funcionarios(self):
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

    def adicionar_loja(self, session, loja):
        if loja not in self.lojas_gerenciadas:
            self.lojas_gerenciadas.append(loja)
            session.commit()
            print(f"Loja '{loja.nome}' adicionada ao gerenciamento de {self.nome}.")
        else:
            print("Essa loja já está sendo gerenciada.")

    def remover_loja(self, session, loja):
        if loja in self.lojas_gerenciadas:
            self.lojas_gerenciadas.remove(loja)
            session.commit()
            print(f"Loja '{loja.nome}' removida do gerenciamento de {self.nome}.")
        else:
            print("Essa loja não está na lista de lojas gerenciadas.")

    def gerar_relatorio_loja(self, loja):
        if loja in self.lojas_gerenciadas:
            total_vendas = sum(pedido.total for pedido in loja.pedidos)
            print(f"Relatório da loja '{loja.nome}':")
            print(f"- Total de vendas: R${total_vendas:.2f}")
            print(f"- Funcionários ativos: {len(loja.funcionarios)}")
            for funcionario in loja.funcionarios:
                print(f"  - {funcionario.nome}, Cargo: {funcionario.cargo}")
        else:
            print("Essa loja não está sob sua gerência.")

    def ajustar_estoque(self, loja_nome, produto_nome, quantidade):
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


class Pedido(Base):
    __tablename__ = 'pedidos'
    
    id = Column(Integer, primary_key=True)
    cliente_id = Column(Integer, ForeignKey('clientes.id'), nullable=False)
    funcionario_id = Column(Integer, ForeignKey('funcionarios.id'), nullable=False)
    loja_id = Column(Integer, ForeignKey('lojas.id'), nullable=False)  # Adicionando a chave estrangeira
    itens = Column(String, nullable=False)  # Armazena como JSON para persistência
    valor_total = Column(Float, default=0.0)
    metodo_pagamento = Column(String, nullable=True)
    data = Column(Date, default=datetime.now)
    status = Column(String, default="Pendente")

    loja = relationship("Loja", back_populates="pedidos")  # Relacionamento com Loja

    def __init__(self, cliente_id, funcionario_id, loja_id):
        self.cliente_id = cliente_id
        self.funcionario_id = funcionario_id
        self.loja_id = loja_id  # Agora o pedido está vinculado à loja
        self.itens = {}

    def adicionar_item(self, item, quantidade, preco_unitario):
        """Adiciona um item ao pedido."""
        if item in self.itens:
            self.itens[item][0] += quantidade
        else:
            self.itens[item] = [quantidade, preco_unitario]
        self.calcular_total()
        print(f"Item {item} adicionado ao pedido.")

    def gerar_nota_fiscal(self):
        """Gera um arquivo de nota fiscal para o pedido."""
        # Definindo o nome do arquivo baseado no ID do pedido
        nome_arquivo = f"nota_fiscal_pedido_{self.id}.txt"
        
        # Verificando se o diretório de notas fiscais existe, se não, cria o diretório
        if not os.path.exists("notas_fiscais"):
            os.makedirs("notas_fiscais")
        
        # Caminho completo do arquivo
        caminho_arquivo = os.path.join("notas_fiscais", nome_arquivo)
        
        # Dados para a nota fiscal
        dados_nota = f"""
        ======= NOTA FISCAL =======
        ID do Pedido: {self.id}
        Cliente: {self.cliente.nome}
        Funcionario: {self.funcionario.nome}
        Data: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}
        
        Itens:
        """
        
        for item in self.itens:
            dados_nota += f"- {item['nome']} (Quantidade: {item['quantidade']}, Preço: R${item['preco']:0.2f})\n"
        
        dados_nota += f"\nValor Total: R${self.valor_total:0.2f}"
        dados_nota += f"\nMétodo de Pagamento: {self.metodo_pagamento}"
        dados_nota += "\n\n================================"
        
        # Salvando os dados no arquivo
        with open(caminho_arquivo, 'w') as arquivo:
            arquivo.write(dados_nota)
        
        print(f"Nota fiscal gerada com sucesso! Caminho: {caminho_arquivo}")

    def remover_item(self, item):
        """Remove um item do pedido."""
        if item in self.itens:
            del self.itens[item]
            self.calcular_total()
            print(f"Item {item} removido do pedido.")
        else:
            print(f"Item {item} não encontrado no pedido.")

    def calcular_total(self):
        """Calcula o valor total do pedido."""
        self.valor_total = sum(qtd * preco for qtd, preco in self.itens.values())
        print(f"Total atualizado: R${self.valor_total:.2f}")

    def finalizar_pedido(self, metodo_pagamento):
        """Finaliza o pedido, confirmando o pagamento."""
        if not self.itens:
            print("O pedido está vazio. Adicione itens antes de finalizar.")
            return
        self.metodo_pagamento = metodo_pagamento
        self.status = "Pago"
        print(f"Pedido finalizado com sucesso. Método de pagamento: {metodo_pagamento}")

    def cancelar_pedido(self):
        """Cancela o pedido."""
        self.status = "Cancelado"
        print(f"Pedido ID {self.id} cancelado.")

    def exibir_detalhes(self):
        """Exibe os detalhes do pedido."""
        print(f"Pedido ID: {self.id}")
        print(f"Cliente ID: {self.cliente_id}")
        print(f"Funcionário ID: {self.funcionario_id}")
        print("Itens:")
        for item, (quantidade, preco) in self.itens.items():
            print(f"- {item}: {quantidade} x R${preco:.2f}")
        print(f"Total: R${self.valor_total:.2f}")
        print(f"Status: {self.status}")
        print(f"Data: {self.data}")

    def alterar_status(self, status):
        """Altera o status do pedido."""
        self.status = status
        print(f"Status do pedido atualizado para: {status}")

    @staticmethod
    def buscar_pedidos_por_cliente(cliente_id, session):
        """Busca todos os pedidos de um cliente específico."""
        pedidos = session.query(Pedido).filter_by(cliente_id=cliente_id).all()
        if pedidos:
            print(f"Pedidos do cliente ID {cliente_id}:")
            for pedido in pedidos:
                print(f"- Pedido ID {pedido.id}: Total R${pedido.valor_total:.2f}, Status: {pedido.status}")
        else:
            print(f"Nenhum pedido encontrado para o cliente ID {cliente_id}.")

  


class Produto(Base):
    __tablename__ = 'produtos'

    id = Column(Integer, primary_key=True)
    nome = Column(String, nullable=False)
    preco = Column(Float, nullable=False)
    estoque = Column(Integer, default=0)
    loja_id = Column(Integer, ForeignKey('lojas.id'))  # Relacionamento com Loja
    loja = relationship("Loja", back_populates="produtos")  # Relacionamento com Loja

    def __init__(self, nome, preco, estoque, loja_id):
        self.nome = nome
        self.preco = preco
        self.estoque = estoque
        self.loja_id = loja_id

    def adicionar_produto(self, session):
        """Adiciona um novo produto ao banco de dados."""
        session.add(self)
        session.commit()
        print(f"Produto {self.categoria} adicionado com sucesso!")

    @staticmethod
    def remover_produto(produto_id, session):
        """Remove um produto do banco de dados."""
        produto = session.query(Produto).get(produto_id)
        if produto:
            session.delete(produto)
            session.commit()
            print(f"Produto ID {produto_id} removido com sucesso!")
        else:
            print(f"Produto ID {produto_id} não encontrado.")

    @staticmethod
    def ajustar_estoque(self, quantidade, session):
        """Ajusta o estoque de um produto (adicionando ou removendo)."""
        if self.estoque + quantidade < 0:
            print(f"Não é possível remover {quantidade} unidades, estoque insuficiente.")
            return
        self.estoque += quantidade
        session.commit()
        print(f"Estoque do produto {self.nome} ajustado para {self.estoque} unidades.")

    @staticmethod
    def consultar_produto(produto_id, session):
        """Consulta os detalhes de um produto específico."""
        produto = session.query(Produto).get(produto_id)
        if produto:
            print(f"Detalhes do Produto ID {produto_id}:")
            print(f"Categoria: {produto.categoria}")
            print(f"Preço: R${produto.preco:.2f}")
            print(f"Estoque: {produto.estoque}")
            print(f"Fornecedor: {produto.fornecedor}")
            print(f"Loja ID: {produto.loja_id}")
        else:
            print(f"Produto ID {produto_id} não encontrado.")

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

    @staticmethod
    def buscar_produtos_por_categoria(categoria, session):
        """Busca todos os produtos de uma determinada categoria."""
        produtos = session.query(Produto).filter_by(categoria=categoria).all()
        if produtos:
            print(f"Produtos na categoria {categoria}:")
            for produto in produtos:
                print(f"- Produto ID {produto.id}: {produto.categoria}, R${produto.preco:.2f}, Estoque: {produto.estoque}")
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
                print(f"- Produto ID {produto.id}: {produto.categoria}, R${produto.preco:.2f}, Estoque: {produto.estoque}")
        else:
            print(f"Nenhum produto encontrado na Loja ID {loja_id}.")

class Remedio(Base):
    __tablename__ = 'remedios'

    id_remedio = Column(Integer, primary_key=True)
    nome = Column(String, nullable=False)
    tarja = Column(String, nullable=False)
    necessita_receita = Column(Boolean, nullable=False)
    validade = Column(Date, nullable=False)

    def __init__(self, nome, categoria, preco, estoque, fornecedor, loja_id, tarja, necessita_receita, validade):
        super().__init__(categoria, preco, estoque, fornecedor, loja_id)
        self.nome = nome
        self.tarja = tarja
        self.necessita_receita = necessita_receita
        self.validade = validade

    def verificar_validade(self):
        """Verifica se o remédio está dentro do prazo de validade."""
        from datetime import date
        if self.validade >= date.today():
            print(f"O remédio {self.nome} está dentro do prazo de validade.")
            return True
        else:
            print(f"O remédio {self.nome} está vencido!")
            return False

    def verificar_necessidade_receita(self):
        """Retorna se o remédio exige receita médica."""
        if self.necessita_receita:
            print(f"O remédio {self.nome} exige receita médica.")
            return True
        else:
            print(f"O remédio {self.nome} não exige receita médica.")
            return False

    def consultar_informacoes(self):
        """Consulta informações detalhadas do remédio."""
        print(f"Informações do Remédio:")
        print(f"- Nome: {self.nome}")
        print(f"- Categoria: {self.categoria}")
        print(f"- Tarja: {self.tarja}")
        print(f"- Exige Receita: {'Sim' if self.necessita_receita else 'Não'}")
        print(f"- Preço: R${self.preco:.2f}")
        print(f"- Estoque: {self.estoque}")
        print(f"- Validade: {self.validade}")

    def atualizar_validade(self, nova_validade):
        """Atualiza a validade do remédio."""
        self.validade = nova_validade
        print(f"A validade do remédio {self.nome} foi atualizada para {self.validade}.")

    @staticmethod
    def listar_remedios_por_tarja(tarja, session):
        """Lista todos os remédios com base na tarja especificada."""
        remedios = session.query(Remedio).filter_by(tarja=tarja).all()
        if remedios:
            print(f"Remédios com tarja {tarja}:")
            for remedio in remedios:
                print(f"- {remedio.nome}, R${remedio.preco:.2f}, Estoque: {remedio.estoque}, Validade: {remedio.validade}")
        else:
            print(f"Nenhum remédio encontrado com tarja {tarja}.")

    def verificar_disponibilidade_em_estoque(self, qtd):
        """Verifica se há quantidade suficiente em estoque."""
        if self.estoque >= qtd:
            print(f"Quantidade disponível para o remédio {self.nome}.")
            return True
        else:
            print(f"Estoque insuficiente para o remédio {self.nome}. Disponível: {self.estoque}")
            return False

class Caixa:
    __tablename__ = 'caixas'

    id = Column(Integer, primary_key=True)
    loja_id = Column(Integer, nullable=False)
    saldo = Column(Float, default=0.0)
    entradas = Column(Float, default=0.0)
    saidas = Column(Float, default=0.0)

    def __init__(self, loja_id):
        self.loja_id = loja_id

    def registrar_entrada(self, valor, session):
        """Registra uma entrada de dinheiro no caixa."""
        if valor <= 0:
            raise ValueError("O valor da entrada deve ser positivo.")
        self.entradas += valor
        self.saldo += valor
        session.commit()
        print(f"Entrada registrada: {valor} - Novo saldo: {self.saldo}")

    def registrar_saida(self, valor, session):
        """Registra uma saída de dinheiro do caixa."""
        if valor <= 0:
            raise ValueError("O valor da saída deve ser positivo.")
        if valor > self.saldo:
            raise ValueError("Saldo insuficiente no caixa.")
        self.saidas += valor
        self.saldo -= valor
        session.commit()
        print(f"Saída registrada: {valor} - Novo saldo: {self.saldo}")

    def consultar_saldo(self):
        """Consulta o saldo atual do caixa."""
        print(f"Saldo atual do caixa: {self.saldo}")
        return self.saldo

    def fechar_caixa(self, session):
        """Fecha o caixa, gerando um relatório."""
        relatorio = {
            "Entradas": self.entradas,
            "Saídas": self.saidas,
            "Saldo Final": self.saldo
        }
        print("Relatório do fechamento do caixa:")
        for key, value in relatorio.items():
            print(f"{key}: {value}")
        self.entradas = 0
        self.saidas = 0
        self.saldo = 0
        session.commit()
        return relatorio

    def transferir_valor(self, valor, caixa_destino, session):
        """Transfere um valor de um caixa para outro caixa."""
        if valor <= 0:
            raise ValueError("O valor a ser transferido deve ser positivo.")
        if valor > self.saldo:
            raise ValueError("Saldo insuficiente no caixa para realizar a transferência.")
        
        self.registrar_saida(valor, session)
        caixa_destino.registrar_entrada(valor, session)
        print(f"Transferido {valor} de caixa {self.id} para caixa {caixa_destino.id}")

    def relatorio_caixa(self):
        """Gera um relatório de entradas, saídas e saldo atual."""
        print(f"Relatório do Caixa {self.id}:")
        print(f"Entradas: {self.entradas}")
        print(f"Saídas: {self.saidas}")
        print(f"Saldo Final: {self.saldo}")

    def consultar_entradas(self):
        """Consulta o total de entradas registradas no caixa."""
        print(f"Total de entradas: {self.entradas}")
        return self.entradas

    def consultar_saidas(self):
        """Consulta o total de saídas registradas no caixa."""
        print(f"Total de saídas: {self.saidas}")
        return self.saidas


class Faturamento:
    __tablename__ = 'faturamentos'

    id = Column(Integer, primary_key=True)
    loja_id = Column(Integer, nullable=False)
    periodo = Column(String, nullable=False)
    valor_total = Column(Float, default=0.0)

    def __init__(self, loja_id, periodo):
        self.loja_id = loja_id
        self.periodo = periodo

    def calcular_faturamento(self, vendas, session):
        """Calcula o faturamento com base nas vendas realizadas."""
        total_faturamento = sum([venda.valor_total for venda in vendas])
        self.valor_total = total_faturamento
        session.commit()
        print(f"Faturamento calculado para o período {self.periodo}: {self.valor_total}")
        return total_faturamento

    def consultar_faturamento(self):
        """Consulta o faturamento total da loja no período."""
        print(f"Faturamento de {self.periodo}: {self.valor_total}")
        return self.valor_total

    def consultar_faturamento_por_periodo(self, periodo, session):
        """Consulta o faturamento de um período específico."""
        faturamento = session.query(Faturamento).filter_by(periodo=periodo, loja_id=self.loja_id).first()
        if faturamento:
            print(f"Faturamento para o período {periodo}: {faturamento.valor_total}")
            return faturamento.valor_total
        else:
            print(f"Faturamento não encontrado para o período {periodo}.")
            return None

    def gerar_relatorio_faturamento(self):
        """Gera um relatório detalhado de faturamento da loja."""
        print(f"Relatório de Faturamento - Loja {self.loja_id} - Período {self.periodo}")
        print(f"Valor Total: {self.valor_total}")
        # Aqui podemos adicionar mais detalhes, como a lista de vendas, etc.
        return {
            "Loja ID": self.loja_id,
            "Período": self.periodo,
            "Faturamento Total": self.valor_total
        }

    def atualizar_faturamento(self, vendas, session):
        """Atualiza o faturamento com base nas vendas realizadas."""
        novo_faturamento = self.calcular_faturamento(vendas, session)
        self.valor_total = novo_faturamento
        session.commit()
        print(f"Faturamento atualizado para o período {self.periodo}: {self.valor_total}")
    
    def calcular_faturamento_mensal(self, loja_id, session):
        """Calcula o faturamento mensal de uma loja específica."""
        from datetime import datetime
        mes_atual = datetime.now().strftime("%B %Y")  # Exemplo: "Janeiro 2024"
        faturamento_mes = session.query(Faturamento).filter_by(loja_id=loja_id, periodo=mes_atual).first()
        
        if faturamento_mes:
            print(f"Faturamento mensal para {mes_atual}: {faturamento_mes.valor_total}")
            return faturamento_mes.valor_total
        else:
            print(f"Faturamento mensal não encontrado para {mes_atual}.")
            return 0

class Cliente:
    __tablename__ = 'clientes'

    id = Column(Integer, primary_key=True)
    nome = Column(String, nullable=False)
    cpf = Column(String, unique=True, nullable=False)
    telefone = Column(String, nullable=False)
    email = Column(String, nullable=False)
    endereco = Column(String, nullable=True)
    historico_compras = Column(Integer, default=0)
    cartao_fidelidade = Column(Integer, ForeignKey('cartao_fidelidade.id'), nullable=True)
    nivel_fidelidade = Column(String, default="Bronze")
    
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

    def consultar_historico(self):
        """Exibe o histórico de compras do cliente."""
        print(f"Histórico de compras do cliente {self.nome}: {self.historico_compras} compras realizadas.")
        return self.historico_compras

    def acumular_pontos_fidelidade(self, valor_compra, pontos_por_reais=1):
        """Acumula pontos de fidelidade com base no valor da compra."""
        pontos_acumulados = valor_compra * pontos_por_reais
        print(f"Cliente {self.nome} acumulou {pontos_acumulados} pontos de fidelidade.")
        self.historico_compras += pontos_acumulados

    def listar_clientes(self, session):
        """Lista todos os clientes cadastrados no sistema."""
        clientes = session.query(Cliente).all()
        for cliente in clientes:
            print(f"ID: {cliente.id}, Nome: {cliente.nome}, Nível de Fidelidade: {cliente.nivel_fidelidade}")
        return clientes

    def atualizar_nivel_fidelidade(self):
        """Atualiza o nível de fidelidade do cliente com base no histórico de compras."""
        if self.historico_compras >= 1000:
            self.nivel_fidelidade = "Ouro"
        elif self.historico_compras >= 500:
            self.nivel_fidelidade = "Prata"
        else:
            self.nivel_fidelidade = "Bronze"
        print(f"Nível de fidelidade do cliente {self.nome} atualizado para {self.nivel_fidelidade}.")

    def calcular_desconto(self, valor_total):
        """Calcula o desconto baseado no nível de fidelidade do cliente."""
        if self.nivel_fidelidade == "Ouro":
            desconto = valor_total * 0.15  # 15% de desconto
        elif self.nivel_fidelidade == "Prata":
            desconto = valor_total * 0.10  # 10% de desconto
        else:
            desconto = valor_total * 0.05  # 5% de desconto
        print(f"Desconto para {self.nivel_fidelidade}: {desconto}")
        return desconto

    def aplicar_desconto(self, valor_total):
        """Aplica o desconto ao valor total da compra."""
        desconto = self.calcular_desconto(valor_total)
        valor_com_desconto = valor_total - desconto
        print(f"Valor com desconto: {valor_com_desconto}")
        return valor_com_desconto

    def verificar_pontos_fidelidade(self):
        """Verifica o total de pontos de fidelidade acumulados."""
        print(f"Cliente {self.nome} tem {self.historico_compras} pontos de fidelidade acumulados.")
        return self.historico_compras

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

class CartaoFidelidade:
    __tablename__ = 'cartao_fidelidade'

    id = Column(Integer, primary_key=True)
    cliente_id = Column(Integer, ForeignKey('clientes.id'), nullable=False)
    desconto = Column(String, nullable=True)  # Ex: "10%" ou "R$ 50"
    beneficios = Column(String, nullable=True)  # Ex: "Frete grátis", "Promoções exclusivas"
    nome = Column(String, nullable=False)  # Ex: "Fidelidade Ouro"

    def __init__(self, cliente_id, nome, desconto=None, beneficios=None):
        self.cliente_id = cliente_id
        self.nome = nome
        self.desconto = desconto
        self.beneficios = beneficios

    def cadastrar_cliente(self, session):
        """Cadastra o cartão de fidelidade para o cliente."""
        session.add(self)
        session.commit()
        print(f"Cartão de Fidelidade '{self.nome}' cadastrado com sucesso para o cliente ID: {self.cliente_id}.")

    def aplicar_desconto(self, valor_total):
        """Aplica o desconto associado ao cartão no valor total da compra."""
        if self.desconto:
            if '%' in self.desconto:
                desconto_percentual = float(self.desconto.replace('%', '')) / 100
                valor_com_desconto = valor_total * (1 - desconto_percentual)
            elif 'R$' in self.desconto:
                desconto_valor = float(self.desconto.replace('R$', '').replace(' ', ''))
                valor_com_desconto = valor_total - desconto_valor
            else:
                valor_com_desconto = valor_total
            print(f"Desconto de {self.desconto} aplicado. Novo valor: {valor_com_desconto:.2f}")
            return valor_com_desconto
        else:
            print("Sem desconto disponível para o cartão.")
            return valor_total

    def consultar_beneficios(self):
        """Exibe os benefícios associados ao cartão de fidelidade."""
        if self.beneficios:
            print(f"Benefícios para o cartão '{self.nome}': {self.beneficios}")
        else:
            print(f"O cartão '{self.nome}' não possui benefícios associados.")
        return self.beneficios

    def atualizar_beneficios(self, beneficios):
        """Atualiza os benefícios do cartão de fidelidade."""
        self.beneficios = beneficios
        print(f"Benefícios do cartão '{self.nome}' atualizados para: {self.beneficios}.")

    def atualizar_desconto(self, desconto):
        """Atualiza o desconto do cartão de fidelidade."""
        self.desconto = desconto
        print(f"Desconto do cartão '{self.nome}' atualizado para: {self.desconto}.")

# Definindo o caminho do banco de dados SQLite (ou outro, se preferir)
engine = create_engine('sqlite:///farmasil.db', echo=True)  # Altere o nome do arquivo conforme necessário

# Criando as tabelas no banco de dados (caso ainda não existam)
Base.metadata.create_all(engine)

# Criando a sessão para interagir com o banco de dados
Session = sessionmaker(bind=engine)
session = Session()

def menu_principal(session):
    while True:
        print("\n==== Sistema Farmasil ====")
        print("1. Gerenciar Loja")
        print("2. Gerenciar Caixa")
        print("3. Gerenciar Faturamento")
        print("4. Gerenciar Clientes")
        print("5. Gerenciar Cartão Fidelidade")
        print("6. Gerenciar Pedidos")
        print("0. Sair")
        opcao = input("Escolha uma opção: ")

        if opcao == "1":
            menu_loja(session)  # Passar session
        elif opcao == "2":
            menu_caixa(session)  # Passar session
        elif opcao == "3":
            menu_faturamento(session)  # Passar session
        elif opcao == "4":
            menu_cliente(session)  # Passar session
        elif opcao == "5":
            menu_cartao_fidelidade(session)  # Passar session
        elif opcao == "6":
            menu_pedido(session)  # Passar session
        elif opcao == "0":
            print("Saindo do sistema...")
            session.close()
            sys.exit()
        else:
            print("Opção inválida! Tente novamente.")

def menu_loja(session):
    while True:
        print("\n==== Gerenciar Loja ====")
        print("1. Adicionar Loja")
        print("2. Atualizar Dados da Loja")
        print("3. Consultar Dados da Loja")
        print("4. Listar Lojas")
        print("5. Consultar Funcionários da Loja")
        print("6. Verificar Estoque da Loja")
        print("7. Alterar Horário de Funcionamento")
        print("8. Remover Loja")
        print("0. Voltar")
        
        opcao = input("Escolha uma opção: ")

        if opcao == "1":
            # Adicionar Loja
            endereco = input("Endereço: ")
            telefone = int(input("Telefone: "))
            horario = input("Horário de Funcionamento: ")
            loja = Loja(endereco=endereco, telefone=telefone, hora_funcionamento=horario)
            loja.adicionar_loja(session)
        
        elif opcao == "2":
            # Atualizar Dados da Loja
            loja_id = int(input("ID da loja a atualizar: "))
            loja = session.query(Loja).filter_by(id=loja_id).first()
            if loja:
                endereco = input(f"Novo Endereço (atual: {loja.endereco}): ") or loja.endereco
                telefone = input(f"Novo Telefone (atual: {loja.telefone}): ") or loja.telefone
                horario = input(f"Novo Horário (atual: {loja.hora_funcionamento}): ") or loja.hora_funcionamento
                loja.atualizar_dados(session, endereco, telefone, horario)
            else:
                print("Loja não encontrada!")
        
        elif opcao == "3":
            # Consultar Dados da Loja
            loja_id = int(input("ID da loja a consultar: "))
            loja = session.query(Loja).filter_by(id=loja_id).first()
            if loja:
                loja.consultar_dados()
            else:
                print("Loja não encontrada!")
        
        elif opcao == "4":
            # Listar Todas as Lojas
            Loja.listar_dados(session)
        
        elif opcao == "5":
            # Consultar Funcionários da Loja
            loja_id = int(input("ID da loja: "))
            loja = session.query(Loja).filter_by(id=loja_id).first()
            if loja:
                loja.consultar_funcionarios_loja(session)
            else:
                print("Loja não encontrada!")
        
        elif opcao == "6":
            # Verificar Estoque da Loja
            loja_id = int(input("ID da loja: "))
            loja = session.query(Loja).filter_by(id=loja_id).first()
            if loja:
                loja.verificar_estoque_loja(session)
            else:
                print("Loja não encontrada!")
        
        elif opcao == "7":
            # Alterar Horário de Funcionamento da Loja
            loja_id = int(input("ID da loja a alterar horário: "))
            loja = session.query(Loja).filter_by(id=loja_id).first()
            if loja:
                novo_horario = input(f"Novo horário (atual: {loja.hora_funcionamento}): ")
                loja.alterar_hora_funcionamento(novo_horario, session)
            else:
                print("Loja não encontrada!")
        
        elif opcao == "8":
            # Remover Loja
            loja_id = int(input("ID da loja a remover: "))
            loja = session.query(Loja).filter_by(id=loja_id).first()
            if loja:
                loja.remover_loja(session)
            else:
                print("Loja não encontrada!")
        
        elif opcao == "0":
            # Voltar para o menu principal
            break
        
        else:
            print("Opção inválida! Tente novamente.")


def menu_caixa(session):
    while True:
        print("\n==== Gerenciar Caixa ====")
        print("1. Registrar Entrada")
        print("2. Registrar Saída")
        print("3. Consultar Saldo")
        print("4. Fechar Caixa")
        print("5. Gerar Relatório do Caixa")
        print("6. Consultar Entradas")
        print("7. Consultar Saídas")
        print("8. Transferir Valor entre Caixas")
        print("0. Voltar")
        
        opcao = input("Escolha uma opção: ")

        if opcao == "1":
            # Registrar Entrada
            valor = float(input("Valor da Entrada: "))
            caixa_id = int(input("ID do Caixa: "))
            caixa = session.query(Caixa).filter_by(id=caixa_id).first()
            if caixa:
                caixa.registrar_entrada(valor, session)
            else:
                print("Caixa não encontrado!")

        elif opcao == "2":
            # Registrar Saída
            valor = float(input("Valor da Saída: "))
            caixa_id = int(input("ID do Caixa: "))
            caixa = session.query(Caixa).filter_by(id=caixa_id).first()
            if caixa:
                caixa.registrar_saida(valor, session)
            else:
                print("Caixa não encontrado!")

        elif opcao == "3":
            # Consultar Saldo
            caixa_id = int(input("ID do Caixa: "))
            caixa = session.query(Caixa).filter_by(id=caixa_id).first()
            if caixa:
                caixa.consultar_saldo()
            else:
                print("Caixa não encontrado!")

        elif opcao == "4":
            # Fechar Caixa
            caixa_id = int(input("ID do Caixa: "))
            caixa = session.query(Caixa).filter_by(id=caixa_id).first()
            if caixa:
                caixa.fechar_caixa(session)
            else:
                print("Caixa não encontrado!")

        elif opcao == "5":
            # Gerar Relatório do Caixa
            caixa_id = int(input("ID do Caixa: "))
            caixa = session.query(Caixa).filter_by(id=caixa_id).first()
            if caixa:
                caixa.relatorio_caixa()
            else:
                print("Caixa não encontrado!")

        elif opcao == "6":
            # Consultar Entradas
            caixa_id = int(input("ID do Caixa: "))
            caixa = session.query(Caixa).filter_by(id=caixa_id).first()
            if caixa:
                caixa.consultar_entradas()
            else:
                print("Caixa não encontrado!")

        elif opcao == "7":
            # Consultar Saídas
            caixa_id = int(input("ID do Caixa: "))
            caixa = session.query(Caixa).filter_by(id=caixa_id).first()
            if caixa:
                caixa.consultar_saidas()
            else:
                print("Caixa não encontrado!")

        elif opcao == "8":
            # Transferir Valor entre Caixas
            caixa_id_origem = int(input("ID do Caixa de Origem: "))
            caixa_origem = session.query(Caixa).filter_by(id=caixa_id_origem).first()
            if caixa_origem:
                caixa_id_destino = int(input("ID do Caixa de Destino: "))
                caixa_destino = session.query(Caixa).filter_by(id=caixa_id_destino).first()
                if caixa_destino:
                    valor_transferencia = float(input("Valor a ser transferido: "))
                    try:
                        caixa_origem.transferir_valor(valor_transferencia, caixa_destino, session)
                    except ValueError as e:
                        print(e)
                else:
                    print("Caixa de destino não encontrado!")
            else:
                print("Caixa de origem não encontrado!")

        elif opcao == "0":
            # Voltar para o menu principal
            break

        else:
            print("Opção inválida! Tente novamente.")


def menu_faturamento(session):
    while True:
        print("\n==== Gerenciar Faturamento ====")
        print("1. Calcular Faturamento para o Período")
        print("2. Consultar Faturamento")
        print("3. Atualizar Faturamento")
        print("4. Gerar Relatório de Faturamento")
        print("5. Consultar Faturamento Mensal")
        print("0. Voltar")
        
        opcao = input("Escolha uma opção: ")

        if opcao == "1":
            # Calcular Faturamento para o Período
            periodo = input("Informe o período para cálculo do faturamento: ")
            loja_id = int(input("Informe o ID da Loja: "))
            vendas = []  # Aqui incluiríamos a consulta de vendas para o período
            faturamento = session.query(Faturamento).filter_by(loja_id=loja_id, periodo=periodo).first()
            if not faturamento:
                faturamento = Faturamento(loja_id=loja_id, periodo=periodo)
            total_faturamento = faturamento.calcular_faturamento(vendas, session)
            print(f"Total do faturamento para o período {periodo}: {total_faturamento}")

        elif opcao == "2":
            # Consultar Faturamento
            loja_id = int(input("Informe o ID da Loja: "))
            periodo = input("Informe o período para consulta: ")
            faturamento = session.query(Faturamento).filter_by(loja_id=loja_id, periodo=periodo).first()
            if faturamento:
                faturamento.consultar_faturamento()
            else:
                print("Faturamento não encontrado para esse período!")

        elif opcao == "3":
            # Atualizar Faturamento
            periodo = input("Informe o período para atualizar o faturamento: ")
            loja_id = int(input("Informe o ID da Loja: "))
            vendas = []  # Aqui incluiríamos a consulta de vendas para o período
            faturamento = session.query(Faturamento).filter_by(loja_id=loja_id, periodo=periodo).first()
            if faturamento:
                faturamento.atualizar_faturamento(vendas, session)
            else:
                print("Faturamento não encontrado para esse período!")

        elif opcao == "4":
            # Gerar Relatório de Faturamento
            loja_id = int(input("Informe o ID da Loja: "))
            periodo = input("Informe o período para gerar o relatório: ")
            faturamento = session.query(Faturamento).filter_by(loja_id=loja_id, periodo=periodo).first()
            if faturamento:
                faturamento.gerar_relatorio_faturamento()
            else:
                print("Faturamento não encontrado para esse período!")

        elif opcao == "5":
            # Consultar Faturamento Mensal
            loja_id = int(input("Informe o ID da Loja: "))
            faturamento_mensal = Faturamento.calcular_faturamento_mensal(loja_id, session)
            print(f"Faturamento mensal: {faturamento_mensal}")

        elif opcao == "0":
            # Voltar para o menu principal
            break

        else:
            print("Opção inválida! Tente novamente.")


def menu_cliente(session):
    while True:
        print("\n==== Gerenciar Clientes ====")
        print("1. Adicionar Cliente")
        print("2. Consultar Cliente")
        print("3. Acumular Pontos de Fidelidade")
        print("4. Listar Todos os Clientes")
        print("5. Atualizar Dados do Cliente")
        print("6. Verificar Pontos de Fidelidade")
        print("7. Remover Cliente")
        print("0. Voltar")
        
        opcao = input("Escolha uma opção: ")

        if opcao == "1":
            # Adicionar Cliente
            nome = input("Nome: ")
            cpf = input("CPF: ")
            telefone = input("Telefone: ")
            email = input("Email: ")
            endereco = input("Endereço (opcional): ")
            cliente = Cliente(nome=nome, cpf=cpf, telefone=telefone, email=email, endereco=endereco)
            cliente.adicionar_cliente(session)

        elif opcao == "2":
            # Consultar Cliente
            cliente_id = int(input("ID do Cliente: "))
            cliente = session.query(Cliente).filter_by(id=cliente_id).first()
            if cliente:
                cliente.consultar_historico()
            else:
                print("Cliente não encontrado!")

        elif opcao == "3":
            # Acumular Pontos de Fidelidade
            cliente_id = int(input("ID do Cliente: "))
            valor_compra = float(input("Valor da Compra: "))
            cliente = session.query(Cliente).filter_by(id=cliente_id).first()
            if cliente:
                cliente.acumular_pontos_fidelidade(valor_compra)
            else:
                print("Cliente não encontrado!")

        elif opcao == "4":
            # Listar Todos os Clientes
            clientes = Cliente.listar_clientes(session)
            for cliente in clientes:
                print(f"ID: {cliente.id}, Nome: {cliente.nome}, Nível de Fidelidade: {cliente.nivel_fidelidade}")

        elif opcao == "5":
            # Atualizar Dados do Cliente
            cliente_id = int(input("ID do Cliente: "))
            nome = input("Novo Nome (deixe em branco para não alterar): ")
            telefone = input("Novo Telefone (deixe em branco para não alterar): ")
            email = input("Novo Email (deixe em branco para não alterar): ")
            endereco = input("Novo Endereço (deixe em branco para não alterar): ")
            cliente = session.query(Cliente).filter_by(id=cliente_id).first()
            if cliente:
                cliente.atualizar_dados_cliente(nome, telefone, email, endereco)
            else:
                print("Cliente não encontrado!")

        elif opcao == "6":
            # Verificar Pontos de Fidelidade
            cliente_id = int(input("ID do Cliente: "))
            cliente = session.query(Cliente).filter_by(id=cliente_id).first()
            if cliente:
                cliente.verificar_pontos_fidelidade()
            else:
                print("Cliente não encontrado!")

        elif opcao == "7":
            # Remover Cliente
            cliente_id = int(input("ID do Cliente: "))
            cliente = session.query(Cliente).filter_by(id=cliente_id).first()
            if cliente:
                cliente.remover_cliente(session)
            else:
                print("Cliente não encontrado!")

        elif opcao == "0":
            # Voltar para o menu principal
            break

        else:
            print("Opção inválida! Tente novamente.")


def menu_cartao_fidelidade(session):
    while True:
        print("\n==== Gerenciar Cartão Fidelidade ====")
        print("1. Cadastrar Cartão Fidelidade")
        print("2. Aplicar Desconto no Valor Total da Compra")
        print("3. Consultar Benefícios do Cartão")
        print("4. Atualizar Desconto do Cartão")
        print("5. Atualizar Benefícios do Cartão")
        print("0. Voltar")
        
        opcao = input("Escolha uma opção: ")

        if opcao == "1":
            # Cadastrar Cartão Fidelidade
            cliente_id = int(input("ID do Cliente: "))
            nome = input("Nome do Cartão: ")
            desconto = input("Desconto (opcional): ")
            beneficios = input("Benefícios (opcional): ")
            cartao = CartaoFidelidade(cliente_id=cliente_id, nome=nome, desconto=desconto, beneficios=beneficios)
            cartao.cadastrar_cliente(session)

        elif opcao == "2":
            # Aplicar Desconto no Valor Total da Compra
            cartao_id = int(input("ID do Cartão: "))
            valor_total = float(input("Valor total da compra: "))
            cartao = session.query(CartaoFidelidade).filter_by(id=cartao_id).first()
            if cartao:
                cartao.aplicar_desconto(valor_total)
            else:
                print("Cartão não encontrado!")

        elif opcao == "3":
            # Consultar Benefícios do Cartão
            cartao_id = int(input("ID do Cartão: "))
            cartao = session.query(CartaoFidelidade).filter_by(id=cartao_id).first()
            if cartao:
                cartao.consultar_beneficios()
            else:
                print("Cartão não encontrado!")

        elif opcao == "4":
            # Atualizar Desconto do Cartão
            cartao_id = int(input("ID do Cartão: "))
            novo_desconto = input("Novo Desconto (opcional): ")
            cartao = session.query(CartaoFidelidade).filter_by(id=cartao_id).first()
            if cartao:
                cartao.atualizar_desconto(novo_desconto)
            else:
                print("Cartão não encontrado!")

        elif opcao == "5":
            # Atualizar Benefícios do Cartão
            cartao_id = int(input("ID do Cartão: "))
            novos_beneficios = input("Novos Benefícios: ")
            cartao = session.query(CartaoFidelidade).filter_by(id=cartao_id).first()
            if cartao:
                cartao.atualizar_beneficios(novos_beneficios)
            else:
                print("Cartão não encontrado!")

        elif opcao == "0":
            # Voltar para o menu principal
            break

        else:
            print("Opção inválida! Tente novamente.")


def menu_pedido(session):
    while True:
        print("\n==== Gerenciar Pedidos ====")
        print("1. Realizar Pedido")
        print("2. Finalizar Pedido")
        print("3. Gerar Nota Fiscal")
        print("4. Adicionar Item ao Pedido")
        print("5. Remover Item do Pedido")
        print("6. Alterar Status do Pedido")
        print("7. Consultar Pedidos de um Cliente")
        print("0. Voltar")
        
        opcao = input("Escolha uma opção: ")

        if opcao == "1":
            # Realizar Pedido
            cliente_id = int(input("ID do Cliente: "))
            funcionario_id = int(input("ID do Funcionário: "))
            pedido = Pedido(cliente_id=cliente_id, funcionario_id=funcionario_id)
            session.add(pedido)
            session.commit()
            print(f"Pedido ID {pedido.id} criado com sucesso!")

        elif opcao == "2":
            # Finalizar Pedido
            pedido_id = int(input("ID do Pedido: "))
            pedido = session.query(Pedido).filter_by(id=pedido_id).first()
            if pedido:
                metodo_pagamento = input("Método de pagamento (Ex: Cartão, Dinheiro, etc.): ")
                pedido.finalizar_pedido(metodo_pagamento)
                session.commit()
            else:
                print("Pedido não encontrado!")

        elif opcao == "3":
            # Gerar Nota Fiscal
            pedido_id = int(input("ID do Pedido: "))
            pedido = session.query(Pedido).filter_by(id=pedido_id).first()
            if pedido:
                pedido.gerar_nota_fiscal()
            else:
                print("Pedido não encontrado!")

        elif opcao == "4":
            # Adicionar Item ao Pedido
            pedido_id = int(input("ID do Pedido: "))
            pedido = session.query(Pedido).filter_by(id=pedido_id).first()
            if pedido:
                item = input("Nome do Item: ")
                quantidade = int(input("Quantidade: "))
                preco_unitario = float(input("Preço unitário: "))
                pedido.adicionar_item(item, quantidade, preco_unitario)
                session.commit()
            else:
                print("Pedido não encontrado!")

        elif opcao == "5":
            # Remover Item do Pedido
            pedido_id = int(input("ID do Pedido: "))
            pedido = session.query(Pedido).filter_by(id=pedido_id).first()
            if pedido:
                item = input("Nome do Item a remover: ")
                pedido.remover_item(item)
                session.commit()
            else:
                print("Pedido não encontrado!")

        elif opcao == "6":
            # Alterar Status do Pedido
            pedido_id = int(input("ID do Pedido: "))
            pedido = session.query(Pedido).filter_by(id=pedido_id).first()
            if pedido:
                novo_status = input("Novo status do pedido (Ex: Pago, Cancelado, etc.): ")
                pedido.alterar_status(novo_status)
                session.commit()
            else:
                print("Pedido não encontrado!")

        elif opcao == "7":
            # Consultar Pedidos de um Cliente
            cliente_id = int(input("ID do Cliente: "))
            Pedido.buscar_pedidos_por_cliente(cliente_id, session)

        elif opcao == "0":
            # Voltar para o menu principal
            break

        else:
            print("Opção inválida! Tente novamente.")


def realizar_pedido(session):
    cliente = input("Digite o nome do cliente: ")
    funcionario = input("Digite o nome do funcionário: ")
    itens = input("Digite os itens do pedido (separados por vírgula): ").split(',')
    valor_total = float(input("Digite o valor total do pedido: R$ "))
    metodo_pagamento = input("Digite o método de pagamento: ")

    pedido = Pedido(id=1, cliente=cliente, funcionario=funcionario, itens=itens, valor_total=valor_total, metodo_pagamento=metodo_pagamento, data=datetime.now().strftime("%Y-%m-%d"))
    session.add(pedido)
    session.commit()
    print(f"Pedido de {cliente} realizado com sucesso!")

def finalizar_pedido(session):
    pedido_id = input("Digite o ID do pedido a ser finalizado: ")
    pedido = session.query(Pedido).filter_by(id=pedido_id).first()
    if pedido:
        pedido.finalizar_pedido()
    else:
        print("Pedido não encontrado!")

def gerar_nota_fiscal(session):
    pedido_id = input("Digite o ID do pedido para gerar a nota fiscal: ")
    pedido = session.query(Pedido).filter_by(id=pedido_id).first()
    if pedido:
        pedido.gerar_nota_fiscal()
    else:
        print("Pedido não encontrado!")

# Inicializar a interface do usuário
menu_principal(session)