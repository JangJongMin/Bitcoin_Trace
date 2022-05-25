import networkx as nx
import streamlit as st
from streamlit_agraph import agraph, Config
from Module.crawling import checkaddress
from Struct.prototype import transaction
from log.bitcoin_tracing_logger import Bitcoin_logger

Bitcoin_logger.set_level('DEBUG')
#st.write("bc1qvzquqqazwh0ctt67z0y8m7esuw6786vje2emfp5m3eypn85ad68q9tez3x")
st.title('BitCoin Transcation Trace System')
address = st.text_input('BitCoin Address Input', 'Address input Please')

def create_node(depth):
    print("Create Node!")
    transaction_class = transaction(address, maxdepth=depth)
    transaction_class.crawling()
    transaction_class.create_node()
    config = Config(width=1000, 
                    height=1000,
                    directed=True,
                    nodeHighlightBehavior=True, 
                    highlightColor="#F7A7A6",
                    collapsible=True,
                    node={'labelProperty':'label'},
                    link={'labelProperty': 'label', 'renderLabel': True},
                    maxZoom=2,
                    minZoom=0.1,
                    staticGraphWithDragAndDrop=False,
                    staticGraph=False,
                    initialZoom=1
                    ) 

    return_value = agraph(nodes=transaction_class.nodes, 
                        edges=transaction_class.edges, 
                        config=config)
    
depth = st.slider('Depth', 1, 11, 1)


if st.button('Search Address : {}'.format(address)):
    with st.spinner('Wait for it...'):
        if checkaddress(address):
            create_node(depth-1)
        else:
            st.write('Wrong Address')
            st.warning("Checking Address")