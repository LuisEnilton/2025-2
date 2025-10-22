### **Resumo Estruturado: Utilização de Prompts e Engenharia de Prompts**

#### 1. **Introdução à Engenharia de Prompts**
- **O que é?** A prática de criar e refinar instruções de entrada para otimizar as saídas de um modelo de IA generativa.
- **Objetivo:** Melhorar a qualidade, relevância e segurança das respostas, reduzindo custos e evitando retreinamento do modelo.

#### 2. **Melhores Práticas para Criação de Prompts**
- Seja **claro e conciso**.
- Inclua **contexto relevante**.
- Use **diretivas específicas**.
- Defina **requisitos de saída**.
- Forneça **exemplos de resposta**.
- Use **tags** para estruturar o prompt.

#### 3. **Elementos Comuns de um Prompt Estruturado**
- **Descrição da tarefa**: O que o modelo deve fazer.
- **Instruções ou etapas**: Como realizar a tarefa.
- **Formato da resposta**: Estrutura desejada da saída.
- **Contexto ou cenário**: Informações de fundo.
- **Persona ou tom**: Voz ou estilo a ser adotado.
- **Público-alvo**: Para quem a resposta é direcionada.
- **Restrições ou exclusões**: O que não deve ser incluído.

#### 4. **Técnicas de Prompting**
- **Zero-shot, Single-shot, Few-shot**: Uso de zero, um ou vários exemplos.
- **Baseado em ferramentas**: Direciona o uso de uma ferramenta específica.
- **Orientado a ações**: Instruções diretas.
- **Negativo**: Explicita o que deve ser excluído.
- **Cadeia de Pensamento (CoT)**: Passos lógicos para raciocínio.
- **Árvore de Pensamento (ToT)**: Múltiplos caminhos ou cenários.
- **Refinamento de Saída**: Iteração, reordenação, filtragem e edição.

#### 5. **Riscos de Prompts Adversos**
- **Injeção de Prompt**: Inserção de comandos maliciosos.
- **Vazamento de Prompt**: Obtenção de informações internas do sistema.
- **Jailbreaking**: Burlar restrições éticas.
- **Engenharia Social**: Manipulação para obter informações sensíveis.

#### 6. **Funcionalidades do Amazon Bedrock para Engenharia de Prompts**
- **Chat/Text Playground**: Ambiente para testar e comparar modelos.
- **Gerenciamento de Prompts**: Criação e versionamento de prompts reutilizáveis.
- **Guardrails**: Filtros para bloquear conteúdos indesejados e ataques adversos.

#### 7. **Atividades Práticas e Verificação de Conhecimento**
- Uso do **PartyRock** (AWS Bedrock Playground) para praticar:
  - Estruturação de prompts.
  - Aplicação de técnicas de prompting.
- **Verificação de conhecimento** com 5 perguntas.
- **Exemplo de questão de exame** com foco em segurança (ex.: uso do Guardrails contra injeção de prompts).

### **Pontos Mais Importantes Destacados**
- A **engenharia de prompts** é essencial para obter melhores resultados com modelos de IA generativa.
- **Estruturar o prompt** com clareza e contexto melhora a coerência e a relevância.
- Técnicas como **Chain of Thought** e **Few-shot** são poderosas para tarefas complexas.
- **Riscos adversos** como injeção e jailbreaking exigem medidas de segurança como o **Amazon Bedrock Guardrails**.
- O **Amazon Bedrock** oferece ferramentas robustas para experimentação, versionamento e proteção de prompts.
