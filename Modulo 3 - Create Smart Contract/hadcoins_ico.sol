// ICO Hadcoins

//versao
pragma solidity ^0.4.11;

contract hadcoin_ico{
    // Número maximo de hadcoins disponiveis no ICO
    uint public max_hadcoins = 1000000;

    // Taxa de cotação de hadcoins para dolar
    uint public usd_to_hadcoins = 1000;

    // Total de hadcoins comprados por investidores
    uint public total_hadcoins_bought = 0;

    // Funções de equivalencia
    mapping(address => uint) equity_hadcoins;
    mapping(address => uint) equity_usd;

    //  Verifica se o investidor pode realizar a compra
    modifier can_buy_hadcoins(uint usd_invested){
        require(usd_invested * usd_to_hadcoins + total_hadcoins_bought <= max_hadcoins);
        _; // comando responsável por aplicar a função somente se a condição for verdadeira
    }

    // Converte o valor do investimento em hadcoins
    function equity_in_hadcoins(address investor) external constant returns(uint){
        return equity_hadcoins[investor];
    }

    // Converte o valor do investimento em usd
    function equity_in_usd(address investor) external constant returns(uint){
        return equity_usd[investor];
    }

    // Compra de hadcoins
    function buy_hadcoins(address investor, uint usd_invested) external 
    can_buy_hadcoins(usd_invested){
        uint hadcoins_bougth = usd_invested *  usd_to_hadcoins;
        equity_hadcoins[investor] += hadcoins_bougth;
        equity_usd[investor] = equity_hadcoins[investor] / 1000;
        total_hadcoins_bought += hadcoins_bougth;
    }

    // Venda de hadcoins
    function sell_hadcoins(address investor, uint hadcoins_sold) external{
        equity_hadcoins[investor] -= hadcoins_sold;
        equity_usd[investor] = equity_hadcoins[investor] / 1000;
        total_hadcoins_bought -= hadcoins_sold;
    }
}