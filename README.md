# BRnotes

**Uma ideia. Um atalho. Uma nota.**

Notas adesivas temporárias para Linux, com aparência de papel, sete cores e abas
que se recolhem nas bordas da tela. Criado e testado no **Fedora KDE Plasma**.

[![Tests](https://github.com/dalvan03/BRnotes/actions/workflows/tests.yml/badge.svg)](https://github.com/dalvan03/BRnotes/actions/workflows/tests.yml)
[![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

![Três notas BRnotes com aparência de papel e exemplos de uso](docs/images/brnotes.png)

> **Notas descartáveis por escolha.** O aplicativo não salva o conteúdo:
> fechar uma nota, encerrar seu processo ou sair da sessão descarta o texto.
> Use para lembretes temporários, não para informações que precisa guardar.

## Funcionalidades

- **Uma nota a cada atalho:** `Meta + Shift + N` abre uma nova janela independente.
- **Sem moldura ou barra de título:** apenas o papel, o seletor de cores e o ×.
- **Aparência de papel:** topo colado, degradê suave, base levemente curva e sombra difusa.
- **Descarte especial:** segure o × por mais de um segundo e solte para amassar e arremessar o papel em uma lixeira.
- **Animações suaves:** abertura, fechamento, recolhimento e restauração em 160–240 ms.
- **Sete cores:** vermelho, laranja, amarelo, verde, azul, anil e violeta em tons suaves.
- **Mover e redimensionar:** arraste o espaço vazio acima do texto ou os limites da nota.
- **Recolher nas quatro bordas:** arraste até uma borda e deixe apenas uma pequena aba visível.
- **Restaurar com um clique:** a aba reabre a nota com o texto e a cor preservados.
- **Edição de texto:** escrever, selecionar, copiar, colar, desfazer e refazer.
- **Sempre à mão:** notas ficam acima das janelas normais.
- **Local e sem conta:** o aplicativo não faz requisições de rede nem grava o texto em arquivos.

## Movimento que combina com papel

A nota aparece com expansão suave, se recolhe até a aba, cresce novamente ao
reabrir e desaparece com uma leve contração ao fechar.

![Demonstração das animações reais do BRnotes](docs/images/animacoes.gif)

## Um papel que vai para a lixeira

Um **clique rápido no ×** mantém o fechamento suave. **Segure o botão esquerdo
no × por mais de um segundo e solte sobre ele** para a animação especial:

1. Uma lixeirinha sobe no canto inferior esquerdo do monitor da nota.
2. A nota se amassa em uma bolinha, preservando sua cor e a textura do texto.
3. A bolinha gira e segue um arco com gravidade constante até a abertura.
4. O papel cai dentro da lixeira, que reage ao impacto e desce para fora da tela.

Um anel no × indica o tempo da pressão. Soltar fora do botão cancela. O efeito
não intercepta cliques no desktop, não cria arquivos na lixeira do sistema e
respeita `BRNOTES_REDUCED_MOTION=1`, usando o fechamento direto nesse modo.

![Papel se amassando e sendo arremessado na lixeira](docs/images/lixeira.gif)

## Sete cores, um círculo

Clique no **círculo multicolorido ao lado do ×**. A cor é independente para cada
nota e também aparece na aba recolhida. Novas notas começam amarelas.

![As sete cores do BRnotes](docs/images/cores.png)

## Libere espaço sem perder a ideia

Arraste a nota para a esquerda, direita, parte superior ou inferior da área útil
do monitor. Ela se transforma em uma aba da mesma cor. Clique para reabrir.
O espaço reservado aos painéis do KDE é respeitado.

![Sequência ilustrada com widgets reais: nota aberta, aba e nota restaurada](docs/images/bordas.png)

*Imagens compostas a partir dos widgets reais do aplicativo, com textos fictícios.
Para regenerá-las: `python3 docs/render_examples.py`.*

## Instalação no Fedora KDE

Requisitos: **Python 3.10+**, **PySide6/Qt 6**, **Pillow**, **X11 ou XWayland** e
**KDE Plasma 6** para a configuração automática do atalho.

```bash
sudo dnf install git python3-pyside6 python3-pillow xorg-x11-server-Xwayland glib2

git clone https://github.com/dalvan03/BRnotes.git
cd BRnotes
/usr/bin/python3 manage.py install
```

Execute o instalador **sem sudo**. Ele instala somente para seu usuário e
adiciona o BRnotes ao menu de aplicativos. O atalho padrão é configurado quando
está disponível; combinações ocupadas por outro aplicativo não são substituídas.
Atalhos do BRnotes já personalizados são preservados.

Agora pressione **Meta + Shift + N**. A tecla Meta costuma ser a tecla Windows/Super.

### Personalizar o atalho

Abra **Configurações do Sistema → Teclado → Atalhos**, procure **BRnotes** e
escolha a combinação desejada. Se não aparecer, adicione o aplicativo BRnotes
pelo seletor de aplicativos dessa tela.

Para instalar sem configurar o atalho automaticamente:

```bash
/usr/bin/python3 manage.py install --no-shortcut
```

### Outras distribuições

O alvo principal é Fedora KDE. Outras distribuições com Plasma 6 e XWayland
podem funcionar, mas ainda não foram validadas manualmente. Instale os equivalentes
das dependências acima ou use um ambiente virtual:

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python manage.py install
```

Nesse caso, mantenha a pasta `.venv`: o lançador usa o interpretador que executou
o instalador. GNOME/Wayland nativo, Windows e macOS não são alvos suportados.
O BRnotes usa o backend XCB do Qt mesmo em sessões Wayland para controlar a
posição das janelas e das abas; uma sessão sem XWayland não é compatível.

## Como usar

| Ação | Como fazer |
| --- | --- |
| Nova nota | `Meta + Shift + N` ou abrir BRnotes pelo menu |
| Escrever | Clique no texto |
| Mudar cor | Clique no círculo multicolorido |
| Mover | Arraste a região vazia acima do texto ou as margens |
| Redimensionar | Arraste os cantos ou limites externos |
| Recolher | Solte próximo a uma borda da área útil do monitor |
| Reabrir | Clique na pequena aba colorida |
| Descartar com animação especial | Segure o **×** por mais de 1 segundo e solte sobre ele |
| Descartar | Clique no **×**; não há confirmação nem salvamento |

Arrastar dentro do editor seleciona texto. O aplicativo não implementa
sincronização, histórico, recuperação ou salvamento automático.

### Reduzir movimento

Para executar sem animações:

```bash
BRNOTES_REDUCED_MOTION=1 /usr/bin/python3 notas.py
```

## Atualizar e desinstalar

Para atualizar a instalação a partir de uma cópia limpa do repositório:

```bash
git pull --ff-only
/usr/bin/python3 manage.py install
```

A atualização vale para novas notas; as já abertas continuam funcionando com a
versão anterior, preservando seu conteúdo em memória.

Para desinstalar, dentro do repositório:

```bash
/usr/bin/python3 manage.py uninstall
```

Sem o repositório, na instalação padrão:

```bash
/usr/bin/python3 ~/.local/share/brnotes/manage.py uninstall
```

O desinstalador remove o lançador, o atalho e os arquivos do aplicativo. Ele não
encerra notas abertas nem remove dependências do sistema. As pastas seguem
`XDG_DATA_HOME` quando essa variável está definida; por padrão, usam `~/.local/share`.

## Desenvolvimento e testes

```bash
/usr/bin/python3 notas.py
/usr/bin/python3 -m unittest discover -s . -v
```

Os testes de interface precisam de uma sessão gráfica e abrem janelas temporárias.
Em ambiente sem desktop, use Xvfb:

```bash
xvfb-run -a -s '-screen 0 1920x1080x24' python3 -m unittest discover -s . -v
```

A suíte cobre edição, colagem, movimento, redimensionamento, recolhimento nas
quatro bordas, restauração, cores independentes, clique curto/longo, cancelamento do descarte, trajetória física,
limpeza da animação e o instalador. A CI usa um
servidor X virtual; ela não substitui a verificação do atalho físico no Plasma.

## Limitações conhecidas

- Duas abas podem se sobrepor quando soltas no mesmo ponto.
- Desconectar monitores durante o uso não tem tratamento específico.
- Escalas diferentes entre monitores e outros compositores precisam de validação.
- Cada nota roda em um processo Python separado; muitas notas aumentam o uso de memória.
- O texto fica na memória do processo. Isso não é uma promessa de isolamento de
  dados em relação à área de transferência, swap ou ferramentas do sistema.

## Comunidade

Encontrou um problema ou tem uma ideia? [Abra uma issue](https://github.com/dalvan03/BRnotes/issues).
Pull requests são bem-vindos; veja [como contribuir](CONTRIBUTING.md).

**Licença [MIT](LICENSE)** — use, modifique e compartilhe, mantendo o aviso da licença.
