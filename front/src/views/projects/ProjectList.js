import React from "react";
import {Table, Row} from "reactstrap";
import Aux from "../../hoc/_Aux";


export default class ProjectList extends React.Component{
    constructor(props) {
        super(props);
    }

    render() {
        return (
                <Row>
                <Table responsive hover striped style={{tableLayout: "fixed"}}>
                <thead>
                <tr>
                    <th style={{whiteSpace: "none"}} width="1%">#</th>
                    <th style={{whiteSpace: "none"}}>Шифр об'єту</th>
                    <th style={{whiteSpace: "none"}}>Адреса об'єкту</th>
                    <th style={{whiteSpace: "none"}}>Тип проекту</th>
                    <th style={{whiteSpace: "none"}}>Договір</th>
                    <th style={{whiteSpace: "none"}}>Статус</th>
                    <th style={{whiteSpace: "none"}}>Керівник проекту</th>
                    <th style={{whiteSpace: "none"}}>Попередження</th>
                </tr>
                </thead>
                <tbody>
                <tr>
                    <td style={{whiteSpace: "none"}} scope="row">1</td>
                    <td style={{whiteSpace: "none"}}>LVI LUT RID</td>
                    <td style={{whiteSpace: "none"}}>Волинська обл., м. Луцьк, вул. Конякіна, 29, ОСББ «КОНЯКІНА 29»</td>
                    <td style={{whiteSpace: "none"}}>28.POS-003 Несуча здатність перекриття ВФ ПП ,,ГАЛКОМСЕРВІС”</td>
                    <td style={{whiteSpace: "none"}}>VF NEW UV GKP ПП ,,ГАЛКОМСЕРВІС”</td>
                    <td style={{whiteSpace: "none"}}>В черзі</td>
                    <td style={{whiteSpace: "none"}}>Кривий Сергій</td>
                    <td style={{whiteSpace: "none"}}>Завершити до 31.07.2020</td>
                </tr>
                </tbody>
            </Table>
                </Row>
        )
    }
}