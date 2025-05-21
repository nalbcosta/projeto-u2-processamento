# 🎮 ShadowRun – A Jornada Pixelada

## 📄 Capa

**Instituição:** UNIT - Universidade Tiradentes (Sergipe)  
**Curso:** Ciência da Computação 
**Disciplina:** Processamento de Imagens  
**Unidade:** Unidade II  
**Aluno(s):**
- Nalbert Schwank Costa Santos
- Luiz Fernando Brito Ferreira
- Heitor Barboza
- Marina Gabriela

**Professora:** Msc. Layse Santos Souza
**Data:** Em andamento (02/06/2025)

---

## 📌 Apresentação

Este projeto é a solução proposta para a Atividade Avaliativa da Unidade 2 da disciplina de Processamento de Imagens. O desafio consistia na criação de um jogo 2D que utilizasse técnicas de computação gráfica e processamento de imagens para criar uma experiência visual e interativa fluida e criativa. O jogo desenvolvido é chamado **ShadowRun**.

---

## 🎯 Objetivos

- Desenvolver um jogo 2D com animações suaves, efeitos visuais e sonoros.
- Ter pelo menos um personagem com caracteristicas e falas.
- Aplicar técnicas de segmentação de imagem usando OpenCV.
- Garantir detecção de colisões com resposta visual e funcional.
- Criar uma experiência de jogo fluida e visualmente agradável.
- Integrar filtros, brilhos, distorções e transições entre elementos.
- Entregar a solução com documentação clara e completa.

---

## 🧠 Metodologia

Para atender aos critérios estabelecidos, o projeto seguiu as etapas abaixo:

1. **Planejamento do jogo**: definição da mecânica, personagens e obstáculos.
2. **Desenvolvimento com Pygame**: criação da base do jogo com movimentação e lógica.
3. **Animações e efeitos**: sprites, sombras, brilhos e transições visuais.
4. **Segmentação de imagem com OpenCV**: usada para aplicar efeitos localizados no personagem.
5. **Implementação sonora**: inclusão de sons para saltos, colisões e eventos.
6. **Testes e ajustes**: verificação da fluidez, colisões e integração dos elementos visuais.

---

## 🛠️ Tecnologias Utilizadas

- 🐍 **Python 3.10+**
- 🎮 **Pygame** – para desenvolvimento do jogo 2D
- 📸 **OpenCV** – para segmentação e manipulação de imagens
- 🎨 **Pillow** – para efeitos e manipulação gráfica
- 🔊 **pygame.mixer** – para sons e trilhas
- 📊 **NumPy** – suporte a arrays e matrizes

---

## 🕹️ Como Jogar

1. Clone este repositório:
   ```bash
   git clone https://github.com/seu-usuario/shadowrun-game.git
   cd shadowrun-game
   ```
2. Instale as dependências:
   ```bash
   pip install -r requirements.txt
   ```
3. Execute o jogo:
   ```bash
   python main.py
   ```
4. Divirta-se!

---

## 🚀 Funcionalidades Implementadas

- Menus (inicial, in-game, game over) com navegação por teclado e trilha sonora dedicada.
- Jogabilidade beat 'em up: movimento lateral, pulo, ataque, múltiplos inimigos com IA e animações completas.
- Três tipos de inimigos: Esqueleto, Cogumelo e Voador, cada um com sprites e comportamentos próprios.
- Sistema de spawn temporizado para inimigos, surgindo progressivamente na fase.
- Sistema de vida do player com invencibilidade temporária após dano e barra de vida na UI.
- Detecção de colisão e resposta visual/sonora (efeitos e sons de impacto).
- Parallax no background para maior profundidade visual.
- UI responsiva com ícones de teclado, legendas e feedback visual aprimorado.
- Transições suaves de música entre menus, fase e combate.
- Efeitos visuais e sonoros integrados.

---

## 📈 Backlog / Linha do Tempo do Projeto

- [x] Estruturação do projeto e setup do Pygame
- [x] Implementação do player com movimento, pulo e ataque
- [x] Criação do menu inicial, menu in-game e game over
- [x] Sistema de animação do player e inimigos (idle, walk, attack, hurt, die)
- [x] Refatoração para beat 'em up: movimento lateral, ataque, IA básica dos inimigos
- [x] Implementação de múltiplos inimigos (Esqueleto, Cogumelo, Voador) com sprites próprios
- [x] Sistema de spawn temporizado para inimigos
- [x] Sistema de vida do player e barra de vida na UI
- [x] Parallax no background
- [x] UI aprimorada com ícones, legendas e responsividade
- [x] Sistema de áudio: SFX, múltiplas trilhas e transições suaves
- [x] Efeitos visuais de impacto e feedback
- [ ] Integração de segmentação de imagem com OpenCV (em andamento)
- [ ] Filtros, brilhos e distorções avançadas (em andamento)
- [ ] Ajustes finais, polimento e documentação

---
