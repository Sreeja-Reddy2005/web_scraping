from bs4 import BeautifulSoup


def test_rating_extraction():
    html = '<p class="star-rating Three"></p>'
    soup = BeautifulSoup(html, "html.parser")
    rating_class = soup.find("p")["class"]
    rating = rating_class[1]
    assert rating == "Three"


def test_upc_extraction():
    html = """
    <table>
        <tr>
            <th>UPC</th>
            <td>abc123</td>
        </tr>
    </table>
    """
    soup = BeautifulSoup(html, "html.parser")
    upc = soup.find("th", string="UPC").find_next("td").text.strip()
    assert upc == "abc123"


def test_description_missing():
    html = "<html></html>"
    soup = BeautifulSoup(html, "html.parser")
    desc_tag = soup.find("div", id="product_description")
    assert desc_tag is None