# System Prompt x User Prompt

A diferença entre `system_prompt` e `user_prompt` pode ser entendida em termos de **arquitetura de interação e controle de contexto/identidade** no *Prompt Engineering*.

Pense nisso como a diferença entre a **configuração do sistema** (as regras e o papel do LLM) e a **entrada do usuário** (o pedido ou a consulta específica).

## Diferença entre `system_prompt` e `user_prompt`

| Recurso | `system_prompt` (Prompt do Sistema) | `user_prompt` (Prompt do Usuário) |
| :--- | :--- | :--- |
| **Objetivo Principal** | **Definir o Papel, Regras e Comportamento** (O *contexto* para o LLM). | **Fazer a Solicitação ou Consulta Específica** (A *entrada* do usuário). |
| **Nível de Controle** | **Meta-controle:** Estabelece a identidade, restrições e o estilo de resposta para *toda* a interação ou sessão. | **Controle de Conteúdo:** Fornece os dados, a pergunta ou a tarefa atual para ser processada. |
| **Posição na Conversa** | **Geralmente o Primeiro e Oculto:** É fornecido ao modelo antes da primeira mensagem do usuário e em cada *turn* subsequente, mas o usuário não o vê. | **Ocorrência Sequencial:** É a mensagem que o usuário envia no fluxo normal de uma conversa ou tarefa. |
| **Exemplo de Uso** | "Você é um especialista socrático em Engenharia de Software. Responda a todas as perguntas como se estivesse desafiando suposições, mantendo as respostas limitadas a 100 palavras e sempre usando notação UML quando apropriado." | "Qual é a diferença entre polimorfismo de inclusão e de subtipo?" |

### 1. `system_prompt` (Prompt do Sistema)

O `system_prompt` é a camada de configuração que atua como uma **instrução de alto nível** para o modelo de linguagem.

* **Definição de Identidade (Persona):** É usado para forçar o LLM a assumir um papel ou personalidade específico ("Você é um assistente de IA prestativo e neutro", "Você é um chef famoso", "Você é um *chatbot* mal-humorado").
* **Restrições e Formato de Saída:** Define as regras rígidas de como o modelo deve gerar a resposta (ex: "Sempre responda em JSON", "Nunca use jargão", "Limitar a saída a bullet points").
* **Contexto Global:** Fornece informações básicas ou contexto que devem ser lembradas e aplicadas a *todas* as interações subsequentes.
* **Mecanismo de Segurança:** Em algumas arquiteturas, pode incluir instruções de segurança (ex: "Nunca gere conteúdo ofensivo ou ilegal").

**Em termos de Arquitetura:** O *system prompt* geralmente é injetado no início do *prompt* de entrada em **cada chamada** à API (embora não seja visível para o usuário final). Ele dita a **função de perda** implícita ou o **objetivo de *sampling*** para o LLM.

### 2. `user_prompt` (Prompt do Usuário)

O `user_prompt` é a entrada direta e visível que o usuário envia ao modelo. Ele contém a **tarefa real** que precisa ser executada.

* **Consulta Direta:** A pergunta ("Quantos estados têm 'Rio' no nome?").
* **Dados de Entrada:** O texto a ser resumido, traduzido ou analisado.
* **Instruções Específicas da Tarefa:** Instruções que se aplicam apenas àquela única solicitação ("Resuma o seguinte texto em três frases...").

**Em termos de Arquitetura:** O *user prompt* é o elemento central do *input* que é concatenado (junto com o histórico da conversa e o `system_prompt`) para formar a entrada final do LLM. O modelo irá processar essa entrada e gerar uma resposta que obedece às regras estabelecidas pelo *system prompt*.

---

## Por Que Essa Separação é Importante (Do Ponto de Vista de Engenharia)

Para um engenheiro de *software* ou cientista da computação:

1.  **Separação de Preocupações (*Separation of Concerns*):**
    * O `system_prompt` trata da **configuração** e do **comportamento** do agente (a camada de serviço).
    * O `user_prompt` trata da **interação** e do **conteúdo** (a camada de *frontend* ou aplicação).
    * Isso torna o sistema mais modular e fácil de manter. Você pode mudar a persona do seu *chatbot* (editando o `system_prompt`) sem alterar a lógica de como ele lida com a entrada do usuário (`user_prompt`).

2.  **Robustez Contra *Prompt Injection*:**
    * Ao definir regras de segurança e formato no `system_prompt`, você está tentando criar uma "cerca" para o modelo. Embora não seja à prova de falhas, essa separação ajuda a mitigar ataques onde um `user_prompt` tenta *sequestrar* o modelo para ignorar as regras.

3.  **Gerenciamento de Contexto Eficiente:**
    * As regras do *system prompt* não precisam ser repetidas na interface do usuário. O engenheiro pode ter certeza de que o modelo sempre terá o contexto primário, independentemente da criatividade do usuário.
